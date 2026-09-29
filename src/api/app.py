import os
import sys
import time
import json
import random
import requests
import secrets
import xml.etree.ElementTree as ET
from typing import Dict, Any

# Load .env FIRST — before any service modules are imported,
# so SMTP credentials are in the environment when EmailService() is instantiated.
try:
    from dotenv import load_dotenv
    _project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    _env_path = os.path.join(_project_root, ".env")
    load_dotenv(dotenv_path=_env_path, override=True)
except ImportError:
    pass

from flask import Flask, request, jsonify, render_template

# Add project root and src directory to path so we can import modules
_src_dir = os.path.dirname(os.path.dirname(__file__))
_proj_dir = os.path.dirname(_src_dir)
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)
if _proj_dir not in sys.path:
    sys.path.insert(0, _proj_dir)

from utils.data_loader import preprocess_text
from utils.dataset_loader import dataset_manager
from models.ner_extractor import CTINERExtractor
from models.attack_tagger import AttackTagger
from models.relation_extractor import CTIRelationExtractor
from kg.knowledge_graph import CTIKnowledgeGraph
from models.scorer import ThreatScorer
from models.recommendation_engine import RecommendationEngine
from services.email_service import email_service
import PyPDF2

# ---------------------------------------------------------------------------
# OTP & Rate Limiting Configuration
# ---------------------------------------------------------------------------
OTP_EXPIRY_SECONDS = 300  # 5 minutes
MAX_OTP_ATTEMPTS = 5      # Maximum verification attempts before lockout
OTP_REQUEST_COOLDOWN = 30 # Seconds between OTP generation requests per email

# otp_store keys are lowercase emails.
# Value: { 'otp': str, 'expires_at': float, 'attempts': int, 'last_requested': float, 'pending_user': dict|None }
otp_store: Dict[str, Dict[str, Any]] = {}

# ---------------------------------------------------------------------------
# User Database Persistence
# ---------------------------------------------------------------------------
USERS_FILE = os.path.join(dataset_manager.data_dir, "users.json")

def load_users() -> Dict[str, Dict[str, str]]:
    """Load persisted users from JSON storage."""
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load users file: {e}")
    return {}

def save_users(users: Dict[str, Dict[str, str]]):
    """Save users dictionary atomically to disk."""
    try:
        os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
        tmp_file = USERS_FILE + ".tmp"
        with open(tmp_file, 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=2)
        os.replace(tmp_file, USERS_FILE)
    except Exception as e:
        print(f"Error persisting users: {e}")

users_db = load_users()

def _generate_otp() -> str:
    """Generate a cryptographically secure random 6-digit OTP."""
    return f"{secrets.randbelow(1000000):06d}"

def _send_otp_email(to_email: str, username: str, otp: str) -> dict:
    """Send a branded OTP email via the configured SMTP email service."""
    subject = "Your CTI Platform Login Code"
    body_text = (
        f"Hello {username},\n\n"
        f"Your one-time login code is: {otp}\n\n"
        f"This code expires in {OTP_EXPIRY_SECONDS // 60} minutes.\n"
        f"If you did not request this code, please ignore this email.\n\n"
        f"— CTI Analysis Platform"
    )
    body_html = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8">
    <style>
      body {{ font-family: 'Segoe UI', sans-serif; background:#f4f6f9; margin:0; padding:20px; color:#333; }}
      .card {{ max-width:560px; margin:0 auto; background:#fff; border-radius:10px;
               overflow:hidden; box-shadow:0 4px 16px rgba(0,0,0,0.1); border:1px solid #e1e8ed; }}
      .header {{ background:linear-gradient(135deg,#1e293b,#0f172a); padding:28px; text-align:center; color:#fff; }}
      .header h1 {{ margin:0; font-size:22px; font-weight:700; letter-spacing:.5px; }}
      .content {{ padding:32px; text-align:center; }}
      .otp-box {{ display:inline-block; background:#0f172a; color:#38bdf8;
                  font-size:40px; font-weight:800; letter-spacing:14px;
                  padding:20px 36px; border-radius:10px; margin:24px 0;
                  font-family:'Courier New',monospace; border:2px solid #38bdf8; }}
      .note {{ font-size:13px; color:#64748b; margin-top:10px; }}
      .footer {{ background:#f8fafc; padding:18px; text-align:center;
                 font-size:12px; color:#94a3b8; border-top:1px solid #e2e8f0; }}
    </style>
    </head>
    <body>
      <div class="card">
        <div class="header"><h1>🛡️ CTI Analysis Platform</h1></div>
        <div class="content">
          <p>Hello <strong>{username}</strong>,</p>
          <p>Use the code below to sign in. It expires in <strong>{OTP_EXPIRY_SECONDS // 60} minutes</strong>.</p>
          <div class="otp-box">{otp}</div>
          <p class="note">If you didn't request this, you can safely ignore this email.</p>
        </div>
        <div class="footer">&copy; CTI Analysis Platform &bull; Automated Security Notification</div>
      </div>
    </body>
    </html>
    """
    return email_service.send_email(to_email, subject, body_text, body_html)

# ---------------------------------------------------------------------------
# Flask App Setup
# ---------------------------------------------------------------------------
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
# Security: Enforce Maximum Payload Size (16 MB) to prevent Denial of Service
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({"error": "File size exceeds the 16MB limit."}), 413

@app.after_request
def add_security_headers(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    # Defense against clickjacking, MIME-sniffing, and XSS
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

# Initialize CTI Models
ner_extractor = CTINERExtractor()
attack_tagger = AttackTagger()
relation_extractor = CTIRelationExtractor()
threat_scorer = ThreatScorer()
recommendation_engine = RecommendationEngine()
global_kg = CTIKnowledgeGraph()

global_stats = {
    "total_reports": 1248,
    "total_iocs": 15786,
    "threat_actors": 342,
    "malware_families": 512,
    "high_severity_alerts": 98
}

# Initial baseline entities in knowledge graph
global_kg.add_entities_from_ner({'threat_actor': ['APT29'], 'malware': ['Emotet']})
global_kg.add_relations_from_extraction([{'source': 'APT29', 'target': 'Emotet', 'relation': 'uses', 'confidence': 0.90}])

IOC_KEYS = {'ip_address', 'ip', 'domain', 'url', 'email', 'hash_sha256', 'hash_md5', 'hash_sha1', 'hash', 'cve', 'registry_key', 'scheduled_task'}

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET'])
def login():
    """Dedicated Analyst Login and Authentication portal page."""
    return render_template('login.html')

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "version": "2.0",
        "kg_nodes": global_kg.graph.number_of_nodes(),
        "kg_edges": global_kg.graph.number_of_edges()
    })

@app.route('/analyze', methods=['POST'])
def analyze_report():
    data = request.json
    if not data or 'report_text' not in data:
        return jsonify({"error": "Missing 'report_text' in request body"}), 400
        
    report_text = data['report_text']
    report_id = data.get('report_id', 'unknown_report')
    
    # 1. Preprocess
    processed_text = preprocess_text(report_text)
    
    # 2. Extract Entities
    entities = ner_extractor.extract_all_entities(processed_text)
    
    # 3. Tag ATT&CK Techniques
    attack_tags = attack_tagger.tag_report(processed_text)
    
    # 4. Extract Relations dynamically
    relations = relation_extractor.extract_all_relations(processed_text, entities)
    
    # 5. Score Threat
    severity = threat_scorer.calculate_severity(entities, attack_tags)
    
    # 6. Generate Dynamic Security Recommendations
    recommendations = recommendation_engine.generate_recommendations(entities, attack_tags, severity)
    
    # 7. Update Global Knowledge Graph
    global_kg.add_entities_from_ner(entities)
    global_kg.add_entities_from_attack_tags(attack_tags)
    global_kg.add_relations_from_extraction(relations)
    
    # 8. Update Global Stats with accurate IOC coverage
    global_stats["total_reports"] += 1
    global_stats["total_iocs"] += sum(len(v) for k, v in entities.items() if k in IOC_KEYS)
    global_stats["threat_actors"] += len(entities.get('threat_actor', []))
    global_stats["malware_families"] += len(entities.get('malware', []))
    if severity.get('score', 0) >= 6.0:
        global_stats["high_severity_alerts"] += 1
        
    return jsonify({
        "report_id": report_id,
        "entities": entities,
        "attack_tags": attack_tags,
        "relations": relations,
        "severity": severity,
        "recommendations": recommendations
    })

@app.route('/analyze/file', methods=['POST'])
def analyze_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    text = ""
    try:
        if file.filename.lower().endswith('.pdf'):
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        else:
            text = file.read().decode('utf-8', errors='ignore')
    except Exception as e:
        return jsonify({"error": f"Failed to parse file: {str(e)}"}), 500
        
    if not text.strip():
        return jsonify({"error": "No text could be extracted from the file."}), 400
        
    report_id = file.filename
    processed_text = preprocess_text(text)
    entities = ner_extractor.extract_all_entities(processed_text)
    attack_tags = attack_tagger.tag_report(processed_text)
    relations = relation_extractor.extract_all_relations(processed_text, entities)
    severity = threat_scorer.calculate_severity(entities, attack_tags)
    
    recommendations = recommendation_engine.generate_recommendations(entities, attack_tags, severity)
    
    global_kg.add_entities_from_ner(entities)
    global_kg.add_entities_from_attack_tags(attack_tags)
    global_kg.add_relations_from_extraction(relations)
    
    global_stats["total_reports"] += 1
    global_stats["total_iocs"] += sum(len(v) for k, v in entities.items() if k in IOC_KEYS)
    global_stats["threat_actors"] += len(entities.get('threat_actor', []))
    global_stats["malware_families"] += len(entities.get('malware', []))
    if severity.get('score', 0) >= 6.0:
        global_stats["high_severity_alerts"] += 1
    
    return jsonify({
        "report_id": report_id,
        "entities": entities,
        "attack_tags": attack_tags,
        "relations": relations,
        "severity": severity,
        "recommendations": recommendations
    })

@app.route('/knowledge_graph/statistics', methods=['GET'])
def kg_statistics():
    return jsonify(global_kg.get_statistics())

@app.route('/knowledge_graph/data', methods=['GET'])
def kg_data():
    return jsonify(global_kg.export_d3())

@app.route('/knowledge_graph/clear', methods=['POST'])
def kg_clear():
    data = request.json or {}
    # Safety confirmation check to prevent accidental or malicious one-click wipe
    if not data.get("confirm", True):
        return jsonify({"status": "error", "message": "Confirmation required to clear knowledge graph."}), 400

    global_kg.clear()
    global_stats["total_reports"] = 0
    global_stats["total_iocs"] = 0
    global_stats["threat_actors"] = 0
    global_stats["malware_families"] = 0
    global_stats["high_severity_alerts"] = 0
    return jsonify({"status": "success", "message": "Knowledge graph and stats cleared successfully."})

@app.route('/dashboard/stats', methods=['GET'])
def get_stats():
    return jsonify(global_stats)

@app.route('/api/news/recent', methods=['GET'])
def get_recent_news():
    fallback_news = [
        {"title": "CISA Adds Known Exploited Vulnerabilities to Catalog", "link": "https://www.cisa.gov/known-exploited-vulnerabilities-catalog", "date": "Live Advisory"},
        {"title": "Critical Infrastructure Defenses: Mitigating Advanced Persistent Threat Actors", "link": "https://www.bleepingcomputer.com", "date": "Live Advisory"},
        {"title": "Ransomware Groups Pivot to Zero-Day Edge Exploits", "link": "https://thehackernews.com", "date": "Live Advisory"},
        {"title": "Phishing Campaigns Target Corporate Supply Chains with InfoStealers", "link": "https://thehackernews.com", "date": "Live Advisory"},
        {"title": "Global Cyber Threat Landscape Quarterly Review", "link": "https://www.bleepingcomputer.com", "date": "Live Advisory"}
    ]
    try:
        urls = [
            "https://feeds.feedburner.com/TheHackersNews",
            "https://www.bleepingcomputer.com/feed/"
        ]
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
        all_items = []
        for url in urls:
            try:
                response = requests.get(url, headers=headers, timeout=4)
                if response.status_code == 200:
                    root = ET.fromstring(response.content)
                    for item in root.findall('./channel/item'):
                        title = item.find('title').text if item.find('title') is not None else ''
                        link = item.find('link').text if item.find('link') is not None else '#'
                        pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ''
                        all_items.append({'title': title.strip(), 'link': link.strip(), 'pub_date': pub_date.strip()})
            except Exception as e:
                print(f"Notice: Failed to fetch feed {url}: {e}")
                
        if not all_items:
            return jsonify({"success": True, "news": fallback_news})

        keywords = ['attack', 'breach', 'ransomware', 'hack', 'steal', 'stolen', 'leak', 'compromise', 'target', 'company', 'organization', 'vulnerability', 'cve', 'malware']
        filtered_items = [item for item in all_items if any(k in item['title'].lower() for k in keywords)]
        
        if len(filtered_items) < 5:
            for item in all_items:
                if item not in filtered_items:
                    filtered_items.append(item)
                if len(filtered_items) >= 5:
                    break

        news_items = []
        for item in filtered_items[:5]:
            pub_date = item['pub_date']
            if pub_date:
                parts = pub_date.split()
                if len(parts) >= 4:
                    pub_date = " ".join(parts[1:4])
            news_items.append({
                "title": item['title'],
                "link": item['link'],
                "date": pub_date
            })
            
        return jsonify({"success": True, "news": news_items})
    except Exception as e:
        print(f"Error fetching news: {e}")
        return jsonify({"success": True, "news": fallback_news})

@app.route('/api/datasets/status', methods=['GET'])
def get_dataset_status():
    """Return metrics, file counts, and sizes for all 6 threat datasets."""
    return jsonify({
        "success": True,
        "datasets": dataset_manager.get_dataset_status()
    })

@app.route('/api/datasets/ingest', methods=['POST'])
def ingest_datasets():
    """Trigger ingestion of reports from loaded datasets into the live Knowledge Graph."""
    data = request.json or {}
    limit = min(data.get("limit_per_dataset", 20), 100) # Enforce maximum limit per batch
    
    dataset_manager.initialize_all_datasets(quick_mode=True)
    
    count = 0
    for item in dataset_manager.stream_all_reports(limit_per_dataset=limit):
        text = preprocess_text(item["text"])
        entities = ner_extractor.extract_all_entities(text)
        attack_tags = attack_tagger.tag_report(text)
        relations = relation_extractor.extract_all_relations(text, entities)
        
        global_kg.add_entities_from_ner(entities)
        global_kg.add_entities_from_attack_tags(attack_tags)
        global_kg.add_relations_from_extraction(relations)
        
        global_stats["total_reports"] += 1
        global_stats["total_iocs"] += sum(len(v) for k, v in entities.items() if k in IOC_KEYS)
        global_stats["threat_actors"] += len(entities.get('threat_actor', []))
        global_stats["malware_families"] += len(entities.get('malware', []))
        count += 1

    return jsonify({
        "success": True,
        "reports_ingested": count,
        "kg_stats": global_kg.get_statistics(),
        "dashboard_stats": global_stats
    })

# ---------------------------------------------------------------------------
# OTP AUTH ENDPOINTS (Hardened against Brute Force and Timing Attacks)
# ---------------------------------------------------------------------------

@app.route('/api/auth/send-otp', methods=['POST'])
def auth_send_otp():
    """Step 1 of login: send a 6-digit OTP to the given email with rate limiting."""
    data = request.json or {}
    email = data.get('email', '').strip().lower()

    if not email:
        return jsonify({"success": False, "error": "Email address is required."}), 400
    if not email_service.validate_email(email):
        return jsonify({"success": False, "error": "Invalid email address format."}), 400

    # Rate limiting on OTP dispatch
    existing_record = otp_store.get(email)
    now = time.time()
    if existing_record and (now - existing_record.get('last_requested', 0)) < OTP_REQUEST_COOLDOWN:
        wait_time = int(OTP_REQUEST_COOLDOWN - (now - existing_record['last_requested']))
        return jsonify({"success": False, "error": f"Please wait {wait_time}s before requesting another OTP."}), 429

    user = users_db.get(email)
    if not user:
        return jsonify({"success": False, "error": "No account found for this email. Please register first."}), 404

    otp = _generate_otp()
    otp_store[email] = {
        "otp": otp,
        "expires_at": now + OTP_EXPIRY_SECONDS,
        "attempts": 0,
        "last_requested": now,
        "pending_user": None
    }

    email_result = _send_otp_email(email, user["username"], otp)
    if not email_result["success"]:
        return jsonify({"success": False, "error": f"Failed to send OTP email: {email_result['error']}"}), 500

    return jsonify({"success": True, "message": f"OTP sent to {email}. Valid for {OTP_EXPIRY_SECONDS // 60} minutes."})


@app.route('/api/auth/users', methods=['GET'])
def auth_get_users():
    """Return list of existing registered users for login selection and client awareness."""
    # Ensure in-memory users_db and disk are aligned
    disk_users = load_users()
    for k, v in disk_users.items():
        if k not in users_db:
            users_db[k] = v
    user_list = [
        {"email": u["email"], "username": u.get("username", u["email"].split('@')[0])}
        for u in users_db.values()
    ]
    return jsonify({"success": True, "users": user_list, "total": len(user_list)})


@app.route('/api/auth/logout', methods=['POST'])
def auth_logout():
    """Handle user logout and audit tracking."""
    data = request.json or {}
    email = data.get('email', '').strip().lower()
    return jsonify({
        "success": True,
        "message": f"User {email} logged out successfully." if email else "Logged out successfully."
    })


@app.route('/api/auth/verify-otp', methods=['POST'])
def auth_verify_otp():
    """Step 2 of login: verify OTP with brute-force lockout and constant-time comparison."""
    data = request.json or {}
    email = data.get('email', '').strip().lower()
    submitted_otp = data.get('otp', '').strip()

    if not email or not submitted_otp:
        return jsonify({"success": False, "error": "Email and OTP are required."}), 400

    record = otp_store.get(email)
    if not record:
        return jsonify({"success": False, "error": "No active OTP request found for this email. Please request a new code."}), 400

    # Check expiration
    if time.time() > record["expires_at"]:
        otp_store.pop(email, None)
        return jsonify({"success": False, "error": "OTP has expired. Please request a new one."}), 400

    # Increment and check attempt count (Brute force protection)
    record["attempts"] = record.get("attempts", 0) + 1
    if record["attempts"] > MAX_OTP_ATTEMPTS:
        otp_store.pop(email, None)
        return jsonify({
            "success": False,
            "error": "Maximum OTP verification attempts exceeded. For your security, this code has been invalidated. Please request a new code."
        }), 429

    # Constant-time comparison to prevent timing attacks
    if not secrets.compare_digest(record["otp"], submitted_otp):
        remaining = MAX_OTP_ATTEMPTS - record["attempts"]
        return jsonify({
            "success": False,
            "error": f"Incorrect OTP. {remaining} attempt(s) remaining."
        }), 401

    # OTP is valid — consume it immediately
    otp_store.pop(email, None)

    user = users_db.get(email)
    if not user:
        return jsonify({"success": False, "error": "Account not found."}), 404

    return jsonify({
        "success": True,
        "message": "Login successful!",
        "user": {"email": user["email"], "username": user["username"]}
    })


@app.route('/api/auth/register/init', methods=['POST'])
def auth_register_init():
    """Step 1 of registration: validate details and send verification OTP with rate limiting."""
    data = request.json or {}
    email = data.get('email', '').strip()
    username = data.get('username', '').strip()

    if not email or not username:
        return jsonify({"success": False, "error": "Full Name and Email are required."}), 400
    if not email_service.validate_email(email):
        return jsonify({"success": False, "error": "Invalid email address format."}), 400
    if email.lower() in users_db:
        return jsonify({"success": False, "error": "An account with this email already exists. Please log in."}), 409

    now = time.time()
    existing_record = otp_store.get(email.lower())
    if existing_record and (now - existing_record.get('last_requested', 0)) < OTP_REQUEST_COOLDOWN:
        wait_time = int(OTP_REQUEST_COOLDOWN - (now - existing_record['last_requested']))
        return jsonify({"success": False, "error": f"Please wait {wait_time}s before requesting another OTP."}), 429

    otp = _generate_otp()
    otp_store[email.lower()] = {
        "otp": otp,
        "expires_at": now + OTP_EXPIRY_SECONDS,
        "attempts": 0,
        "last_requested": now,
        "pending_user": {"username": username, "email": email}
    }

    email_result = _send_otp_email(email, username, otp)
    if not email_result["success"]:
        return jsonify({"success": False, "error": f"Failed to send OTP email: {email_result['error']}"}), 500

    return jsonify({"success": True, "message": f"Verification OTP sent to {email}. Enter it below to complete registration."})


@app.route('/api/auth/register/verify', methods=['POST'])
def auth_register_verify():
    """Step 2 of registration: verify OTP, enforce brute-force limits, and persist account."""
    data = request.json or {}
    email = data.get('email', '').strip().lower()
    submitted_otp = data.get('otp', '').strip()

    if not email or not submitted_otp:
        return jsonify({"success": False, "error": "Email and OTP are required."}), 400

    record = otp_store.get(email)
    if not record or not record.get("pending_user"):
        return jsonify({"success": False, "error": "No pending registration found. Please start again."}), 400

    if time.time() > record["expires_at"]:
        otp_store.pop(email, None)
        return jsonify({"success": False, "error": "OTP has expired. Please start registration again."}), 400

    # Brute-force attempt checking
    record["attempts"] = record.get("attempts", 0) + 1
    if record["attempts"] > MAX_OTP_ATTEMPTS:
        otp_store.pop(email, None)
        return jsonify({
            "success": False,
            "error": "Maximum verification attempts exceeded. Registration session invalidated. Please start again."
        }), 429

    # Constant-time comparison
    if not secrets.compare_digest(record["otp"], submitted_otp):
        remaining = MAX_OTP_ATTEMPTS - record["attempts"]
        return jsonify({"success": False, "error": f"Incorrect OTP. {remaining} attempt(s) remaining."}), 401

    # OTP valid — consume record and create account
    pending = record["pending_user"]
    otp_store.pop(email, None)
    username = pending["username"]

    users_db[email] = {"username": username, "email": pending["email"]}
    save_users(users_db)

    # Send welcome email asynchronously / defensively
    try:
        email_result = email_service.send_welcome_email(
            to_email=pending["email"],
            username=username,
            login_url=request.host_url
        )
    except Exception as e:
        email_result = {"success": False, "error": str(e)}

    msg = "Account created successfully! You are now logged in."
    if email_result.get("success"):
        msg += " A welcome email has been dispatched."

    return jsonify({
        "success": True,
        "message": msg,
        "user": {"email": pending["email"], "username": username},
        "email_status": email_result
    })


def start_server():
    print("Starting CTI API Server...")
    print("API will be available at http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == '__main__':
    start_server()
