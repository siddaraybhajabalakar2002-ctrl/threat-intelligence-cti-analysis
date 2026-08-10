"""
CTI Dataset Loader and Management Utility
Handles downloading, generating, loading, and parsing datasets for the CTI Analysis Pipeline:
1. NVD CVE (~25,000+ vulnerability records)
2. MITRE ATT&CK Framework (Complete Enterprise STIX framework)
3. Security News Articles (5,000-10,000 articles)
4. Phishing Emails (10,000 phishing email samples)
5. IOC Records (50,000+ IP, Domain, Hash, URL indicators)
6. Malware Reports (2,000 malware technical reports)
"""

import os
import json
import csv
import random
import urllib.request
import urllib.error
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")


def preprocess_text(text: str) -> str:
    """Preprocess CTI report text for pipeline ingestion."""
    if not text:
        return ""
    return text.strip()


class DatasetManager:
    """Manager for CTI datasets handling storage, fetching, generation, and retrieval."""

    def __init__(self, data_dir: str = DATA_DIR):
        self.data_dir = data_dir
        self.dirs = {
            "mitre_attack": os.path.join(self.data_dir, "mitre_attack"),
            "nvd_cve": os.path.join(self.data_dir, "nvd_cve"),
            "security_news": os.path.join(self.data_dir, "security_news"),
            "phishing_emails": os.path.join(self.data_dir, "phishing_emails"),
            "iocs": os.path.join(self.data_dir, "iocs"),
            "malware_reports": os.path.join(self.data_dir, "malware_reports"),
        }
        self._ensure_directories()

    def _ensure_directories(self):
        """Create necessary dataset subdirectories if they do not exist."""
        for d in self.dirs.values():
            os.makedirs(d, exist_ok=True)

    def initialize_all_datasets(self, quick_mode: bool = False):
        """Initialize all 6 datasets (downloads online feeds or generates dataset files)."""
        print("[DatasetManager] Initializing dataset subdirectories...")
        self._ensure_directories()

        print("[DatasetManager] 1/6 Setting up MITRE ATT&CK framework dataset...")
        self.setup_mitre_attack()

        print("[DatasetManager] 2/6 Setting up NVD CVE dataset...")
        self.setup_nvd_cve(quick_mode=quick_mode)

        print("[DatasetManager] 3/6 Setting up Security News Articles dataset...")
        self.setup_security_news(quick_mode=quick_mode)

        print("[DatasetManager] 4/6 Setting up Phishing Emails dataset...")
        self.setup_phishing_emails(quick_mode=quick_mode)

        print("[DatasetManager] 5/6 Setting up IOC Records dataset...")
        self.setup_iocs(quick_mode=quick_mode)

        print("[DatasetManager] 6/6 Setting up Malware Reports dataset...")
        self.setup_malware_reports(quick_mode=quick_mode)

        print("[DatasetManager] All datasets successfully set up and ready!")
        return self.get_dataset_status()

    # -------------------------------------------------------------------------
    # 1. MITRE ATT&CK Framework
    # -------------------------------------------------------------------------
    def setup_mitre_attack(self):
        """Download official MITRE ATT&CK STIX framework JSON or fallback to local dataset."""
        dest_file = os.path.join(self.dirs["mitre_attack"], "enterprise_attack.json")
        url = "https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json"
        
        if not os.path.exists(dest_file):
            print("  Downloading official MITRE ATT&CK Enterprise framework...")
            try:
                urllib.request.urlretrieve(url, dest_file)
                print("  Successfully downloaded MITRE ATT&CK framework.")
            except Exception as e:
                print(f"  Warning: Could not fetch online MITRE data ({e}). Generating core ATT&CK dataset.")
                sample_data = {
                    "type": "bundle",
                    "id": "bundle--mitre-attack-enterprise",
                    "objects": [
                        {"type": "attack-pattern", "id": "attack-pattern--T1566", "name": "Phishing", "external_references": [{"external_id": "T1566"}]},
                        {"type": "attack-pattern", "id": "attack-pattern--T1059", "name": "Command and Scripting Interpreter", "external_references": [{"external_id": "T1059"}]},
                        {"type": "attack-pattern", "id": "attack-pattern--T1055", "name": "Process Injection", "external_references": [{"external_id": "T1055"}]},
                        {"type": "attack-pattern", "id": "attack-pattern--T1190", "name": "Exploit Public-Facing Application", "external_references": [{"external_id": "T1190"}]},
                        {"type": "attack-pattern", "id": "attack-pattern--T1071", "name": "Application Layer Protocol", "external_references": [{"external_id": "T1071"}]},
                    ]
                }
                with open(dest_file, "w", encoding="utf-8") as f:
                    json.dump(sample_data, f, indent=2)

    # -------------------------------------------------------------------------
    # 2. NVD CVE Records (~25,000+ vulnerabilities)
    # -------------------------------------------------------------------------
    def setup_nvd_cve(self, quick_mode: bool = False):
        """Setup NVD CVE vulnerability records dataset."""
        dest_file = os.path.join(self.dirs["nvd_cve"], "nvd_cve_records.json")
        if os.path.exists(dest_file):
            return

        count = 1000 if quick_mode else 25000
        print(f"  Generating NVD CVE dataset with {count:,} vulnerability records...")

        vendors = ["Microsoft", "Apache", "Oracle", "Cisco", "Linux", "Apple", "Adobe", "Google", "VMware", "F5"]
        products = ["Windows", "HTTP Server", "Database", "IOS", "Kernel", "macOS", "Acrobat", "Chrome", "ESXi", "BIG-IP"]
        types = ["Remote Code Execution", "Buffer Overflow", "SQL Injection", "Privilege Escalation", "Cross-Site Scripting", "Bypass Authentication"]

        records = []
        for i in range(1, count + 1):
            year = 2020 + (i % 6)
            cve_id = f"CVE-{year}-{1000 + i}"
            vendor = random.choice(vendors)
            product = random.choice(products)
            vuln_type = random.choice(types)
            cvss = round(random.uniform(4.0, 10.0), 1)

            records.append({
                "cve_id": cve_id,
                "vendor": vendor,
                "product": product,
                "description": f"A {vuln_type} vulnerability in {vendor} {product} allows remote attackers to execute arbitrary code or cause a denial of service.",
                "cvss_score": cvss,
                "severity": "CRITICAL" if cvss >= 9.0 else ("HIGH" if cvss >= 7.0 else "MEDIUM"),
                "published_date": f"{year}-{(i%12)+1:02d}-{(i%28)+1:02d}"
            })

        with open(dest_file, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2)

    # -------------------------------------------------------------------------
    # 3. Security News Articles (5,000 - 10,000 articles)
    # -------------------------------------------------------------------------
    def setup_security_news(self, quick_mode: bool = False):
        """Setup Security News & Threat Blog articles dataset."""
        dest_file = os.path.join(self.dirs["security_news"], "security_news_corpus.json")
        if os.path.exists(dest_file):
            return

        count = 500 if quick_mode else 5000
        print(f"  Generating Security News dataset with {count:,} threat articles...")

        actors = ["APT29", "APT28", "Lazarus Group", "FIN7", "LockBit", "BlackCat", "Dragonfly", "Sandworm"]
        malware = ["Cobalt Strike", "Emotet", "Qakbot", "AgentTesla", "FormBook", "RedLine Stealer", "IcedID"]
        sectors = ["Financial Services", "Energy Sector", "Healthcare", "Government", "Defense Industrial Base", "Education"]

        articles = []
        for i in range(1, count + 1):
            actor = random.choice(actors)
            mw = random.choice(malware)
            sector = random.choice(sectors)
            ip = f"{random.randint(1,223)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
            domain = f"threat-{random.randint(100,999)}.{random.choice(['com','org','net','io'])}"
            cve = f"CVE-202{random.randint(0,5)}-{random.randint(1000,9999)}"

            content = (
                f"Security Incident Alert: {actor} has launched a major cyber campaign utilizing {mw} "
                f"against organizations in the {sector}. The attackers exploited {cve} to gain initial access. "
                f"Command and control server observed at {ip} ({domain}). Security teams are advised to block "
                f"network traffic to {domain} immediately."
            )

            articles.append({
                "article_id": f"NEWS-2026-{(i):05d}",
                "title": f"{actor} Campaign Targeting {sector} with {mw}",
                "author": "CyberThreat Analyst",
                "source": "Global Security Watch",
                "text": content,
                "actor": actor,
                "malware": mw,
                "cve": cve,
                "ip": ip,
                "domain": domain
            })

        with open(dest_file, "w", encoding="utf-8") as f:
            json.dump(articles, f, indent=2)

    # -------------------------------------------------------------------------
    # 4. Phishing Emails (10,000 email samples)
    # -------------------------------------------------------------------------
    def setup_phishing_emails(self, quick_mode: bool = False):
        """Setup Phishing Emails dataset."""
        dest_file = os.path.join(self.dirs["phishing_emails"], "phishing_emails.json")
        if os.path.exists(dest_file):
            return

        count = 1000 if quick_mode else 10000
        print(f"  Generating Phishing Emails dataset with {count:,} email samples...")

        subjects = [
            "URGENT: Password Expiration Notice",
            "Invoice Payment Overdue #8921",
            "Security Alert: Unusual sign-in activity",
            "Payroll Details Verification Required",
            "HR Update: Employee Handbook Policy"
        ]

        emails = []
        for i in range(1, count + 1):
            domain = f"login-verify-{random.randint(100,999)}.com"
            sender = f"support@{domain}"
            ip = f"{random.randint(1,223)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
            hash_val = f"{random.getrandbits(256):064x}"

            body = (
                f"Dear User,\n\n"
                f"Your account requires immediate action. Please sign in to http://{domain}/auth/login "
                f"from IP {ip} to verify your credentials. Failure to do so will result in account termination.\n\n"
                f"Attachment Hash: {hash_val}\n"
                f"Regards,\nIT Security Desk"
            )

            emails.append({
                "email_id": f"PHISH-{(i):06d}",
                "sender": sender,
                "subject": random.choice(subjects),
                "body": body,
                "phishing_link": f"http://{domain}/auth/login",
                "ip": ip,
                "attachment_hash": hash_val
            })

        with open(dest_file, "w", encoding="utf-8") as f:
            json.dump(emails, f, indent=2)

    # -------------------------------------------------------------------------
    # 5. Bulk IOC Records (50,000+ IOCs)
    # -------------------------------------------------------------------------
    def setup_iocs(self, quick_mode: bool = False):
        """Setup 50,000+ IOC records dataset (CSV/JSON)."""
        dest_file = os.path.join(self.dirs["iocs"], "bulk_iocs.csv")
        if os.path.exists(dest_file):
            return

        count = 2500 if quick_mode else 50000
        print(f"  Generating IOC Records dataset with {count:,} IOC entries...")

        threat_types = ["c2_server", "malware_drop", "phishing_url", "exfiltration_ip", "ransomware_hash"]
        malware_families = ["LockBit", "Emotet", "CobaltStrike", "AgentTesla", "AsyncRAT", "Mirai"]

        with open(dest_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ioc_type", "value", "threat_category", "malware_family", "confidence_score", "first_seen"])

            for i in range(1, count + 1):
                mod = i % 4
                if mod == 0:
                    ioc_type = "ip"
                    value = f"{random.randint(1,223)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
                elif mod == 1:
                    ioc_type = "domain"
                    value = f"bad-node-{random.randint(1000,99999)}.{random.choice(['biz','xyz','online','top','cc'])}"
                elif mod == 2:
                    ioc_type = "sha256"
                    value = f"{random.getrandbits(256):064x}"
                else:
                    ioc_type = "url"
                    value = f"http://malicious-host-{random.randint(100,999)}.net/payload_{i}.bin"

                writer.writerow([
                    ioc_type,
                    value,
                    random.choice(threat_types),
                    random.choice(malware_families),
                    random.randint(65, 100),
                    f"2026-07-{(i%28)+1:02d}"
                ])

    # -------------------------------------------------------------------------
    # 6. Malware Technical Reports (2,000 reports)
    # -------------------------------------------------------------------------
    def setup_malware_reports(self, quick_mode: bool = False):
        """Setup Technical Malware Reports dataset."""
        dest_file = os.path.join(self.dirs["malware_reports"], "malware_reports.json")
        if os.path.exists(dest_file):
            return

        count = 200 if quick_mode else 2000
        print(f"  Generating Malware Technical Reports dataset with {count:,} reports...")

        family_list = ["WannaCry", "DarkSide", "REvil", "Conti", "TrickBot", "Dridex", "BazarLoader", "RedLine"]
        techniques_list = ["T1059", "T1055", "T1566", "T1071", "T1053", "T1547", "T1041"]

        reports = []
        for i in range(1, count + 1):
            family = random.choice(family_list)
            ip = f"{random.randint(1,223)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
            hash_val = f"{random.getrandbits(256):064x}"
            tech = random.choice(techniques_list)

            text = (
                f"MALWARE ANALYSIS REPORT #{i:04d} - {family}\n"
                f"Malware Family: {family}\n"
                f"Sample Hash: {hash_val}\n"
                f"C2 Infrastructure: {ip}\n"
                f"MITRE ATT&CK Technique: {tech}\n\n"
                f"Technical Analysis:\n"
                f"The malware sample {family} drops persistence in Registry Run keys and injects code "
                f"into svchost.exe using {tech}. It establishes beaconing to C2 server {ip}."
            )

            reports.append({
                "report_id": f"MAL-REP-{(i):04d}",
                "family": family,
                "text": text,
                "sha256": hash_val,
                "c2_ip": ip,
                "technique": tech
            })

        with open(dest_file, "w", encoding="utf-8") as f:
            json.dump(reports, f, indent=2)

    # -------------------------------------------------------------------------
    # Status & Streamers
    # -------------------------------------------------------------------------
    def get_dataset_status(self) -> dict:
        """Return counts and metadata for all 6 datasets."""
        status = {}
        for name, dpath in self.dirs.items():
            files = os.listdir(dpath) if os.path.exists(dpath) else []
            total_size = sum(os.path.getsize(os.path.join(dpath, f)) for f in files if os.path.isfile(os.path.join(dpath, f)))
            status[name] = {
                "directory": dpath,
                "file_count": len(files),
                "total_size_bytes": total_size,
                "size_mb": round(total_size / (1024 * 1024), 2),
                "files": files
            }
        return status

    def stream_all_reports(self, limit_per_dataset: int = 100):
        """Yield CTI text reports from all datasets for pipeline processing."""
        # 1. Security News
        news_file = os.path.join(self.dirs["security_news"], "security_news_corpus.json")
        if os.path.exists(news_file):
            with open(news_file, "r", encoding="utf-8") as f:
                articles = json.load(f)
                for item in articles[:limit_per_dataset]:
                    yield {"id": item.get("article_id"), "text": item.get("text")}

        # 2. Malware Reports
        mal_file = os.path.join(self.dirs["malware_reports"], "malware_reports.json")
        if os.path.exists(mal_file):
            with open(mal_file, "r", encoding="utf-8") as f:
                reports = json.load(f)
                for item in reports[:limit_per_dataset]:
                    yield {"id": item.get("report_id"), "text": item.get("text")}

        # 3. Phishing Emails
        phish_file = os.path.join(self.dirs["phishing_emails"], "phishing_emails.json")
        if os.path.exists(phish_file):
            with open(phish_file, "r", encoding="utf-8") as f:
                emails = json.load(f)
                for item in emails[:limit_per_dataset]:
                    text = f"Phishing Email: {item.get('subject')}\nFrom: {item.get('sender')}\n{item.get('body')}"
                    yield {"id": item.get("email_id"), "text": text}


# Global singleton instance
dataset_manager = DatasetManager()
