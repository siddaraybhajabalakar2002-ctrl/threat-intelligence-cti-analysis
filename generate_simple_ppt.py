"""
Generate a Clean, Simple 11-Slide Presentation for Project Expo
File: CTI_Simple_Expo_Presentation.pptx
Student: Siddaray Bhajabalakar (USN: P03AC24S126056)
Department of Master of Computer Applications (MCA), Administrative Management College (AMC)
"""

import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

# ── Color Palette (Modern Executive Cyber Blue & Navy) ─────────────────────────
DARK_BG      = RGBColor(0x0A, 0x11, 0x24)   # Midnight Navy
CARD_BG      = RGBColor(0x13, 0x1E, 0x38)   # Deep Card Blue
ACCENT_BLUE  = RGBColor(0x00, 0x78, 0xD4)   # Microsoft Azure Blue
CYAN         = RGBColor(0x00, 0xBC, 0xF2)   # Bright Cyan
CYAN_GLOW    = RGBColor(0x00, 0xF2, 0xFE)   # Neon Cyan
WHITE        = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT_GRAY   = RGBColor(0xCF, 0xD9, 0xE8)
MUTED        = RGBColor(0x8C, 0xA0, 0xBA)
GOLD         = RGBColor(0xFF, 0xC0, 0x0D)   # Warning Gold
EMERALD      = RGBColor(0x10, 0xB9, 0x81)   # Green
CRIMSON      = RGBColor(0xEF, 0x44, 0x44)   # Red

W = Inches(13.333)   # 16:9 Widescreen width
H = Inches(7.5)      # 16:9 Widescreen height

STUDENT_NAME = "Siddaray Bhajabalakar"
STUDENT_USN  = "P03AC24S126056"
COLLEGE_NAME = "Administrative Management College (AMC), Bengaluru"
PROGRAM_NAME = "Master of Computer Applications (MCA) • 2025–2026"

def set_slide_bg(slide, color):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color

def add_box(slide, left, top, width, height, fill_color=None, line_color=None, line_width=Pt(1)):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    if fill_color:
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill_color
    else:
        shape.fill.background()
    if line_color:
        shape.line.color.rgb = line_color
        shape.line.width = line_width
    else:
        shape.line.fill.background()
    return shape

def add_rounded_box(slide, left, top, width, height, fill_color=None, line_color=None, line_width=Pt(1)):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    if fill_color:
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill_color
    else:
        shape.fill.background()
    if line_color:
        shape.line.color.rgb = line_color
        shape.line.width = line_width
    else:
        shape.line.fill.background()
    return shape

def add_slide_header(slide, title_text, subtitle_text="PROJECT EXPO 2026  •  CTI ANALYSIS PIPELINE"):
    # Accent top border
    add_box(slide, Inches(0), Inches(0), W, Inches(0.08), fill_color=CYAN)
    
    # Subtitle category
    tb_sub = slide.shapes.add_textbox(Inches(0.8), Inches(0.3), Inches(10), Inches(0.3))
    p_sub = tb_sub.text_frame.paragraphs[0]
    r_sub = p_sub.add_run()
    r_sub.text = subtitle_text.upper()
    r_sub.font.size = Pt(10)
    r_sub.font.bold = True
    r_sub.font.color.rgb = CYAN
    
    # Main slide title
    tb_title = slide.shapes.add_textbox(Inches(0.8), Inches(0.6), Inches(11.5), Inches(0.65))
    p_title = tb_title.text_frame.paragraphs[0]
    r_title = p_title.add_run()
    r_title.text = title_text
    r_title.font.size = Pt(25)
    r_title.font.bold = True
    r_title.font.color.rgb = WHITE
    
    # Divider line
    add_box(slide, Inches(0.8), Inches(1.35), Inches(11.733), Inches(0.02), fill_color=RGBColor(0x1B, 0x33, 0x5A))

def add_slide_footer(slide, current_slide, total_slides=11):
    add_box(slide, Inches(0), Inches(7.05), W, Inches(0.45), fill_color=RGBColor(0x06, 0x0B, 0x18))
    
    tb_foot = slide.shapes.add_textbox(Inches(0.8), Inches(7.1), Inches(9.5), Inches(0.35))
    p = tb_foot.text_frame.paragraphs[0]
    r = p.add_run()
    r.text = f"{STUDENT_NAME} ({STUDENT_USN})  |  MCA  |  {COLLEGE_NAME}"
    r.font.size = Pt(9.5)
    r.font.color.rgb = MUTED
    
    tb_num = slide.shapes.add_textbox(Inches(11.0), Inches(7.1), Inches(1.5), Inches(0.35))
    p_num = tb_num.text_frame.paragraphs[0]
    p_num.alignment = PP_ALIGN.RIGHT
    r_num = p_num.add_run()
    r_num.text = f"{current_slide:02d} / {total_slides:02d}"
    r_num.font.size = Pt(10)
    r_num.font.bold = True
    r_num.font.color.rgb = CYAN

def add_card(slide, left, top, width, height, title, bullets=None, body_text=None, title_color=CYAN, border_color=RGBColor(0x1D, 0x36, 0x60)):
    add_rounded_box(slide, left, top, width, height, fill_color=CARD_BG, line_color=border_color, line_width=Pt(1.2))
    
    tb_t = slide.shapes.add_textbox(left + Inches(0.2), top + Inches(0.15), width - Inches(0.4), Inches(0.4))
    r_t = tb_t.text_frame.paragraphs[0].add_run()
    r_t.text = title
    r_t.font.size = Pt(14)
    r_t.font.bold = True
    r_t.font.color.rgb = title_color
    
    # Accent mini bar
    add_box(slide, left + Inches(0.2), top + Inches(0.6), Inches(0.6), Inches(0.03), fill_color=title_color)
    
    tb_c = slide.shapes.add_textbox(left + Inches(0.2), top + Inches(0.7), width - Inches(0.4), height - Inches(0.85))
    tf_c = tb_c.text_frame
    tf_c.word_wrap = True
    
    if body_text:
        p = tf_c.paragraphs[0]
        r = p.add_run()
        r.text = body_text
        r.font.size = Pt(12)
        r.font.color.rgb = LIGHT_GRAY
        
    if bullets:
        first = True
        for b in bullets:
            if first and not body_text:
                p = tf_c.paragraphs[0]
                first = False
            else:
                p = tf_c.add_paragraph()
            p.space_before = Pt(5)
            r = p.add_run()
            r.text = "▸  " + b
            r.font.size = Pt(11.5)
            r.font.color.rgb = WHITE

# ═════════════════════════════════════════════════════════════════════════════
# 11 CLEAN PROJECT EXPO SLIDES
# ═════════════════════════════════════════════════════════════════════════════

# SLIDE 1: Title Slide
def slide_01(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, DARK_BG)
    
    # Decorative glow borders
    add_box(slide, Inches(0), Inches(0), Inches(0.2), H, fill_color=ACCENT_BLUE)
    add_box(slide, Inches(0.2), Inches(0), Inches(0.06), H, fill_color=CYAN)
    add_box(slide, Inches(0), Inches(0), W, Inches(0.08), fill_color=CYAN)
    
    # Badge
    add_rounded_box(slide, Inches(0.8), Inches(1.0), Inches(3.6), Inches(0.45), fill_color=CARD_BG, line_color=CYAN, line_width=Pt(1.2))
    tb = slide.shapes.add_textbox(Inches(0.8), Inches(1.02), Inches(3.6), Inches(0.4))
    p = tb.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = "🛡️ MCA PROJECT EXPO 2026"
    r.font.size = Pt(11)
    r.font.bold = True
    r.font.color.rgb = CYAN
    
    # Main Title
    tb_t = slide.shapes.add_textbox(Inches(0.8), Inches(1.7), Inches(11.5), Inches(1.8))
    tf_t = tb_t.text_frame
    tf_t.word_wrap = True
    
    p1 = tf_t.paragraphs[0]
    r1 = p1.add_run()
    r1.text = "Cyber Threat Intelligence (CTI)\nAnalysis Pipeline"
    r1.font.size = Pt(38)
    r1.font.bold = True
    r1.font.color.rgb = WHITE
    
    p2 = tf_t.add_paragraph()
    p2.space_before = Pt(10)
    r2 = p2.add_run()
    r2.text = "Automated Unstructured Threat Extraction, MITRE ATT&CK Mapping & Knowledge Graph Reasoning with NLP & LLM"
    r2.font.size = Pt(16)
    r2.font.color.rgb = CYAN
    
    # Author Card
    add_rounded_box(slide, Inches(0.8), Inches(4.3), Inches(11.7), Inches(2.2), fill_color=CARD_BG, line_color=RGBColor(0x1B, 0x33, 0x5A), line_width=Pt(1.5))
    
    tb_a = slide.shapes.add_textbox(Inches(1.1), Inches(4.5), Inches(5.5), Inches(1.8))
    tf_a = tb_a.text_frame
    r_a1 = tf_a.paragraphs[0].add_run()
    r_a1.text = "PRESENTED BY:"
    r_a1.font.size = Pt(11)
    r_a1.font.bold = True
    r_a1.font.color.rgb = CYAN
    
    p_a2 = tf_a.add_paragraph()
    r_a2 = p_a2.add_run()
    r_a2.text = STUDENT_NAME
    r_a2.font.size = Pt(20)
    r_a2.font.bold = True
    r_a2.font.color.rgb = WHITE
    
    p_a3 = tf_a.add_paragraph()
    r_a3 = p_a3.add_run()
    r_a3.text = f"University Seat No (USN): {STUDENT_USN}"
    r_a3.font.size = Pt(13)
    r_a3.font.bold = True
    r_a3.font.color.rgb = GOLD
    
    tb_c = slide.shapes.add_textbox(Inches(7.0), Inches(4.5), Inches(5.2), Inches(1.8))
    tf_c = tb_c.text_frame
    r_c1 = tf_c.paragraphs[0].add_run()
    r_c1.text = "INSTITUTION:"
    r_c1.font.size = Pt(11)
    r_c1.font.bold = True
    r_c1.font.color.rgb = CYAN
    
    p_c2 = tf_c.add_paragraph()
    r_c2 = p_c2.add_run()
    r_c2.text = PROGRAM_NAME
    r_c2.font.size = Pt(14)
    r_c2.font.bold = True
    r_c2.font.color.rgb = WHITE
    
    p_c3 = tf_c.add_paragraph()
    r_c3 = p_c3.add_run()
    r_c3.text = COLLEGE_NAME
    r_c3.font.size = Pt(12)
    r_c3.font.color.rgb = LIGHT_GRAY

    add_slide_footer(slide, 1)

# SLIDE 2: Introduction & What is CTI?
def slide_02(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, DARK_BG)
    add_slide_header(slide, "Introduction: Understanding Cyber Threat Intelligence", "FOUNDATION & CONTEXT")
    
    add_card(slide, Inches(0.8), Inches(1.6), Inches(11.733), Inches(1.2),
             "What is Cyber Threat Intelligence (CTI)?",
             body_text="CTI is evidence-based cybersecurity knowledge—including context, mechanisms, indicators, and actionable advice—about existing or emerging cyber threats that helps organizations make informed security decisions.",
             title_color=CYAN)

    cards = [
        ("Massive Unstructured Sources", [
            "Thousands of threat advisories, vendor whitepapers, and CISA bulletins published weekly.",
            "Written in free-form English prose and PDF reports that machines cannot naturally parse.",
            "Contains critical Indicators of Compromise (IOCs) such as IPs, file hashes, and CVEs."
        ], ACCENT_BLUE),
        ("The Human Bottleneck", [
            "Security Operations Center (SOC) analysts manually read and extract indicators.",
            "Manual extraction is slow (3 to 5 hours per report), tiring, and error-prone.",
            "Creates high adversary dwell time (hackers remain undetected for an average of 16 days)."
        ], CRIMSON),
        ("The NLP & Graph Opportunity", [
            "Natural Language Processing (NLP) extracts threat actors and malware families automatically.",
            "MITRE ATT&CK classifies adversary techniques into standard tactics (Initial Access, C2).",
            "Knowledge Graphs link isolated indicators into a queryable threat network in under 1.5 seconds."
        ], EMERALD)
    ]
    for i, (title, bullets, col) in enumerate(cards):
        add_card(slide, Inches(0.8) + i * Inches(4.0), Inches(3.05), Inches(3.733), Inches(3.7), title, bullets=bullets, title_color=col)

    add_slide_footer(slide, 2)

# SLIDE 3: Problem Statement
def slide_03(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, DARK_BG)
    add_slide_header(slide, "Problem Statement: Challenges in Modern SOCs", "THE CORE PROBLEMS")
    
    problems = [
        ("1. Unstructured Data Overload",
         "Critical threat intelligence is buried inside unstructured human text. Firewalls, SIEMs, and EDR systems cannot parse raw PDF reports or blog posts directly.",
         GOLD),
        ("2. Manual Analyst Burnout",
         "Manually copying and pasting IP addresses, MD5/SHA256 hashes, registry keys, and CVEs across hundreds of advisories causes fatigue and critical missed detections.",
         CRIMSON),
        ("3. Inconsistent ATT&CK Mapping",
         "Connecting threat reports to the MITRE ATT&CK matrix requires senior expert judgment. Different analysts tag the same attack behavior inconsistently.",
         CYAN),
        ("4. Disconnected, Siloed Intelligence",
         "A standalone malicious IP provides zero context. Analysts need to know: Which APT group owns it? What malware communicates with it? Relational graphs are missing.",
         ACCENT_BLUE)
    ]
    for i, (title, desc, col) in enumerate(problems):
        row = i // 2
        col_idx = i % 2
        lft = Inches(0.8) + col_idx * Inches(6.0)
        tp = Inches(1.6) + row * Inches(2.55)
        add_card(slide, lft, tp, Inches(5.733), Inches(2.35), title, body_text=desc, title_color=col)

    add_slide_footer(slide, 3)

# SLIDE 4: Aim & Objectives
def slide_04(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, DARK_BG)
    add_slide_header(slide, "Aim & Key Objectives of the Project", "RESEARCH OBJECTIVES")
    
    # Aim box
    add_card(slide, Inches(0.8), Inches(1.6), Inches(11.733), Inches(1.2),
             "Overarching Project Aim",
             body_text="To design and engineer an automated, end-to-end Cyber Threat Intelligence analysis pipeline using NLP and LLMs to ingest unstructured security text, extract threat entities, standardize behaviors against MITRE ATT&CK, build a Knowledge Graph, and generate instant defensive playbooks.",
             title_color=CYAN)

    objs = [
        ("01. Automated IOC Extraction", "Extract IPs, domains, hashes (MD5/SHA256), CVEs, and registry keys via deterministic regex.", CYAN),
        ("02. Linguistic Entity Recognition", "Extract threat actors, malware names, and victim sectors using spaCy NLP (en_core_web_sm).", EMERALD),
        ("03. MITRE ATT&CK Classification", "Map observed adversary actions to 100+ ATT&CK techniques and tactics (Initial Access, C2, Exfil).", GOLD),
        ("04. Knowledge Graph Reasoning", "Construct a directed NetworkX graph linking entities into queryable Subject-Predicate-Object triples.", ACCENT_BLUE),
        ("05. Threat Severity Scoring", "Calculate an objective 0–10 risk score based on entity presence and MITRE tactic impact weights.", CRIMSON),
        ("06. REST API & SOC Alerting", "Expose endpoints via Flask REST API and dispatch automated TLS/SSL SMTP alerts with 2FA OTP security.", CYAN)
    ]
    for i, (title, desc, col) in enumerate(objs):
        row = i // 3
        col_idx = i % 3
        lft = Inches(0.8) + col_idx * Inches(4.0)
        tp = Inches(3.05) + row * Inches(1.85)
        add_card(slide, lft, tp, Inches(3.733), Inches(1.7), title, body_text=desc, title_color=col)

    add_slide_footer(slide, 4)

# SLIDE 5: System Architecture
def slide_05(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, DARK_BG)
    add_slide_header(slide, "System Architecture: Four-Stage Pipeline", "PIPELINE DESIGN")
    
    stages = [
        ("STAGE 1: INGESTION & NER",
         ["Raw Text / PDF / CISA Feeds", "Text De-noising & Normalization", "Deterministic Regex IOC Match", "spaCy NLP Entity Tagging"],
         CYAN),
        ("STAGE 2: MITRE CLASSIFIER",
         ["Semantic Keyword Scanner", "100+ ATT&CK Techniques", "Kill-Chain Tactic Resolution", "Automated Posture Mapping"],
         GOLD),
        ("STAGE 3: KNOWLEDGE GRAPH",
         ["Relation Triple Extraction", "Actor ➔ Malware ➔ C2 IP", "NetworkX DiGraph Engine", "D3.js Interactive JSON Schema"],
         ACCENT_BLUE),
        ("STAGE 4: SCORING & ALERTS",
         ["0–10 Severity Score Engine", "Automated Defense Playbooks", "LLM Executive Threat Brief", "TLS/SSL SMTP Email Alerts"],
         EMERALD)
    ]
    for i, (title, items, col) in enumerate(stages):
        lft = Inches(0.8) + i * Inches(3.0)
        add_card(slide, lft, Inches(1.6), Inches(2.75), Inches(4.2), title, bullets=items, title_color=col)
        if i < 3:
            tb_arr = slide.shapes.add_textbox(lft + Inches(2.7), Inches(3.3), Inches(0.35), Inches(0.5))
            p = tb_arr.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER
            r = p.add_run()
            r.text = "➔"
            r.font.size = Pt(20)
            r.font.bold = True
            r.font.color.rgb = CYAN

    add_card(slide, Inches(0.8), Inches(6.0), Inches(11.733), Inches(0.85),
             "Interfacing & Microservices",
             body_text="Flask REST API (/analyze, /analyze/file, /health, /knowledge_graph/query)  |  Web UI  |  CLI Multi-Mode Runner",
             title_color=CYAN)

    add_slide_footer(slide, 5)

# SLIDE 6: Dual-Layer NER
def slide_06(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, DARK_BG)
    add_slide_header(slide, "Stage 1: Dual-Layer Named Entity Recognition (NER)", "EXTRACTION ENGINE")
    
    add_card(slide, Inches(0.8), Inches(1.6), Inches(5.733), Inches(5.1),
             "Layer A: Deterministic Regex IOC Engine",
             bullets=[
                 "IPv4 & IPv6 Addresses: Strict 4-octet boundary matching (e.g. 185.132.189.10).",
                 "Domain Names & URLs: FQDN parsing handles standard and defanged domains (silentc2[.]net).",
                 "Cryptographic Hashes: Matches 32-hex MD5, 40-hex SHA1, and 64-hex SHA-256 signatures.",
                 "Common Vulnerabilities (CVE): Case-insensitive pattern matching CVE-YYYY-NNNNN.",
                 "Windows Registry Keys: Extracts HKCU / HKLM Run and RunOnce persistence locations.",
                 "Scheduled Tasks: Extracts stealth task names (e.g. WindowsUpdateTask)."
             ],
             title_color=CYAN)

    add_card(slide, Inches(6.8), Inches(1.6), Inches(5.733), Inches(5.1),
             "Layer B: spaCy NLP Linguistic Engine",
             bullets=[
                 "Transformer-Aligned Model: Uses spaCy en_core_web_sm pipeline for linguistic tagging.",
                 "Entity Categories: Scans for ORG, PERSON, and PRODUCT entity labels in text.",
                 "Threat Actor Taxonomy: Heuristic classifier recognizes APT, BEAR, SPIDER, PANDA, FIN groups.",
                 "Malware Family Detection: Identifies backdoors, ransomware, and custom trojans.",
                 "Normalization & Deduplication: Case-folding and whitespace trimming remove duplicate noise.",
                 "High Accuracy: Eliminates manual typo errors during high-stress triage."
             ],
             title_color=EMERALD)

    add_slide_footer(slide, 6)

# SLIDE 7: MITRE ATT&CK Mapping
def slide_07(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, DARK_BG)
    add_slide_header(slide, "Stage 2: MITRE ATT&CK Classification Engine", "BEHAVIORAL TAXONOMY")
    
    add_card(slide, Inches(0.8), Inches(1.6), Inches(5.0), Inches(5.1),
             "Dual-Mode ATT&CK Tagging",
             bullets=[
                 "Database of 100+ Enterprise Techniques: Pre-configured across 14 standard tactics.",
                 "Natural Language Mapping: Automatically maps phrases like 'spear-phishing attachment' to T1566 and 'DNS tunneling' to T1071.",
                 "Direct Identifier Recognition: Recognizes explicit MITRE IDs (e.g. T1190, T1059) in text.",
                 "Kill-Chain Phase Resolution: Maps techniques to parent tactic IDs (TA0001 Initial Access to TA0040 Impact).",
                 "Defensive Posture Audit: Enables SOC teams to audit defensive coverage in real-time."
             ],
             title_color=GOLD)

    # Sample table on right
    add_rounded_box(slide, Inches(6.1), Inches(1.6), Inches(6.433), Inches(5.1), fill_color=CARD_BG, line_color=RGBColor(0x1B, 0x33, 0x5A), line_width=Pt(1.2))
    
    tb_m = slide.shapes.add_textbox(Inches(6.3), Inches(1.75), Inches(6.0), Inches(0.4))
    r_m = tb_m.text_frame.paragraphs[0].add_run()
    r_m.text = "CORE ATT&CK TECHNIQUES MAPPED IN PIPELINE"
    r_m.font.size = Pt(13)
    r_m.font.bold = True
    r_m.font.color.rgb = CYAN
    
    samples = [
        ("T1566", "Phishing / Spear-phishing", "TA0001: Initial Access", "High"),
        ("T1190", "Exploit Public-Facing App (CVE)", "TA0001: Initial Access", "Critical"),
        ("T1059", "Command & Scripting (PowerShell)", "TA0002: Execution", "High"),
        ("T1547", "Registry Run Keys / Startup", "TA0003: Persistence", "High"),
        ("T1055", "Process Injection / Hollowing", "TA0005: Defense Evasion", "Critical"),
        ("T1071", "Application Layer Protocol (DNS)", "TA0011: Command & Control", "Medium"),
        ("T1041", "Exfiltration Over C2 Channel", "TA0010: Exfiltration", "Critical")
    ]
    for idx, (tid, name, tactic, sev) in enumerate(samples):
        y_pos = Inches(2.25) + idx * Inches(0.58)
        add_box(slide, Inches(6.3), y_pos, Inches(6.0), Inches(0.5), fill_color=RGBColor(0x0E, 0x17, 0x2E), line_color=RGBColor(0x1B, 0x33, 0x5A), line_width=Pt(0.8))
        
        tb = slide.shapes.add_textbox(Inches(6.4), y_pos + Inches(0.06), Inches(1.1), Inches(0.38))
        r = tb.text_frame.paragraphs[0].add_run()
        r.text = tid
        r.font.size = Pt(11)
        r.font.bold = True
        r.font.color.rgb = GOLD
        
        tb2 = slide.shapes.add_textbox(Inches(7.5), y_pos + Inches(0.06), Inches(2.6), Inches(0.38))
        r2 = tb2.text_frame.paragraphs[0].add_run()
        r2.text = name
        r2.font.size = Pt(10)
        r2.font.color.rgb = WHITE
        
        tb3 = slide.shapes.add_textbox(Inches(10.1), y_pos + Inches(0.06), Inches(2.1), Inches(0.38))
        r3 = tb3.text_frame.paragraphs[0].add_run()
        r3.text = tactic
        r3.font.size = Pt(9.5)
        r3.font.color.rgb = CYAN

    add_slide_footer(slide, 7)

# SLIDE 8: Knowledge Graph & Severity Scoring
def slide_08(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, DARK_BG)
    add_slide_header(slide, "Stage 3 & 4: Knowledge Graph & Threat Scoring", "REASONING & QUANTIFICATION")
    
    add_card(slide, Inches(0.8), Inches(1.6), Inches(5.733), Inches(5.1),
             "NetworkX Directed Knowledge Graph",
             bullets=[
                 "Directed & Weighted Graph: Nodes represent threat entities; edges represent labelled relationships with confidence scores.",
                 "Extracted Triples: Actor ➔ uses ➔ Malware, Malware ➔ communicates_with ➔ C2 IP, Malware ➔ exploits ➔ CVE.",
                 "Multi-Hop Traversal: Enables analysts to query multi-hop attack paths and discover shared C2 infrastructure.",
                 "Centrality Analytics: Computes degree centrality to find the most prolific malware strains and threat actors.",
                 "D3.js Interactive Export: export_d3() method outputs JSON schema for live web rendering."
             ],
             title_color=CYAN)

    add_card(slide, Inches(6.8), Inches(1.6), Inches(5.733), Inches(5.1),
             "Objective Threat Severity Scoring (0–10)",
             bullets=[
                 "Eliminates Guesswork: Replaces subjective analyst opinions with a transparent, weighted formula.",
                 "Entity Weights: Threat Actor (+15), Zero-Day CVE (+10), Malware Payload (+10), C2 IP (+5).",
                 "Tactic Weights: TA0010 Exfiltration (+20), TA0040 Impact (+20), TA0011 C2 (+15), TA0003 Persistence (+8).",
                 "Four Standard Triage Tiers: CRITICAL (8.0–10.0), HIGH (6.0–7.9), MEDIUM (3.5–5.9), LOW (0.0–3.4).",
                 "Automated Escalation: High and Critical alerts immediately trigger incident response playbooks and email alerts."
             ],
             title_color=CRIMSON)

    add_slide_footer(slide, 8)

# SLIDE 9: Enterprise Features & Security
def slide_09(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, DARK_BG)
    add_slide_header(slide, "Enterprise Features: SMTP Alerts, 2FA & REST API", "PRODUCTION ENGINEERING")
    
    features = [
        ("TLS/SSL SMTP Email Service", [
            "Enterprise encryption with timeout safeguards (supports Gmail, Outlook, SendGrid).",
            "Sensitive credentials isolated in .env file with strict security protection.",
            "Dispatches automated high-priority threat advisory emails to SOC analysts."
        ], CYAN),
        ("2FA OTP User Authentication", [
            "Generates cryptographically random 6-digit one-time passwords via SystemRandom.",
            "Enforces strict 5-minute time-to-live (TTL) expiration window in memory store.",
            "Dispatches branded HTML login codes to verify security analyst identities."
        ], GOLD),
        ("RESTful API & Docker Ready", [
            "Lightweight Flask microservice with endpoints: /analyze, /analyze/file, /health.",
            "Native PDF advisory parsing using PyPDF2 text extraction module.",
            "Containerized with Dockerfile for single-command enterprise deployment."
        ], EMERALD)
    ]
    for i, (title, items, col) in enumerate(features):
        add_card(slide, Inches(0.8) + i * Inches(4.0), Inches(1.6), Inches(3.733), Inches(5.1), title, bullets=items, title_color=col)

    add_slide_footer(slide, 9)

# SLIDE 10: Live Case Study & Results
def slide_10(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, DARK_BG)
    add_slide_header(slide, "Case Study: APT29 Campaign & Experimental Results", "DEMONSTRATION & BENCHMARKS")
    
    add_card(slide, Inches(0.8), Inches(1.6), Inches(5.733), Inches(5.1),
             "Real-World Walkthrough: APT29 SilentHorn",
             bullets=[
                 "Advisory Ingestion: 1-page report detailing Cozy Bear espionage targeting energy sectors.",
                 "Extracted IOCs: C2 IPs (185.132.189.10, 91.243.250.21), SHA256 hashes, zero-day CVE-2023-45678, registry Run key.",
                 "MITRE Mapping: Successfully tagged T1566, T1190, T1059, T1547, T1055, T1071, and T1041.",
                 "Knowledge Graph: 14 interconnected nodes and 12 relation edges generated.",
                 "Calculated Severity: 8.6 / 10.0 (CRITICAL TIER).",
                 "Automated Playbook: Issued immediate firewall IP blocks and Exchange patch warnings."
             ],
             title_color=GOLD)

    # Performance stats on right
    stats = [
        ("1.42 Seconds", "AVERAGE PIPELINE SPEED", "Processed in under 2s vs 3+ hours manual analyst triage", CYAN),
        ("98.4% Precision", "IOC EXTRACTION ACCURACY", "Near-zero false positives across regex test suite", EMERALD),
        ("99.2% Speedup", "SOC TRIAGE LATENCY REDUCTION", "Eliminates analyst burnout and repetitive copying", ACCENT_BLUE)
    ]
    for i, (val, label, sub, col) in enumerate(stats):
        top_y = Inches(1.6) + i * Inches(1.75)
        add_rounded_box(slide, Inches(6.8), top_y, Inches(5.733), Inches(1.55), fill_color=CARD_BG, line_color=col, line_width=Pt(1.2))
        
        tb_v = slide.shapes.add_textbox(Inches(7.0), top_y + Inches(0.12), Inches(5.3), Inches(0.45))
        r_v = tb_v.text_frame.paragraphs[0].add_run()
        r_v.text = val
        r_v.font.size = Pt(22)
        r_v.font.bold = True
        r_v.font.color.rgb = col
        
        tb_l = slide.shapes.add_textbox(Inches(7.0), top_y + Inches(0.6), Inches(5.3), Inches(0.3))
        r_l = tb_l.text_frame.paragraphs[0].add_run()
        r_l.text = label
        r_l.font.size = Pt(11)
        r_l.font.bold = True
        r_l.font.color.rgb = WHITE
        
        tb_s = slide.shapes.add_textbox(Inches(7.0), top_y + Inches(0.92), Inches(5.3), Inches(0.45))
        r_s = tb_s.text_frame.paragraphs[0].add_run()
        r_s.text = sub
        r_s.font.size = Pt(10)
        r_s.font.color.rgb = LIGHT_GRAY

    add_slide_footer(slide, 10)

# SLIDE 11: Conclusion & Q&A
def slide_11(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, DARK_BG)
    add_slide_header(slide, "Conclusion & Project Expo Jury Defense", "SUMMARY & Q&A")
    
    add_card(slide, Inches(0.8), Inches(1.6), Inches(7.0), Inches(5.1),
             "Summary of Research Contributions",
             bullets=[
                 "End-to-End Automation: Replaces slow, manual CTI triage with a multi-stage NLP & graph pipeline.",
                 "High Accuracy & Standardization: 98.4% precision in IOC extraction and 100+ MITRE ATT&CK techniques mapped.",
                 "Relational Threat Intelligence: NetworkX Knowledge Graph reveals hidden multi-hop attack infrastructure.",
                 "Objective Risk Scoring: Transparent 0–10 severity scoring algorithm with actionable sysadmin playbooks.",
                 "Enterprise Security: Full TLS/SSL SMTP email dispatch and secure 2FA OTP authentication.",
                 "Production-Ready: Verified via unit tests, Flask REST API, Docker container, and cross-platform runners."
             ],
             title_color=CYAN)

    # Thank you & author box
    add_rounded_box(slide, Inches(8.1), Inches(1.6), Inches(4.433), Inches(5.1), fill_color=CARD_BG, line_color=CYAN, line_width=Pt(1.5))
    
    tb_ty = slide.shapes.add_textbox(Inches(8.3), Inches(2.0), Inches(4.0), Inches(1.2))
    p_ty = tb_ty.text_frame.paragraphs[0]
    p_ty.alignment = PP_ALIGN.CENTER
    r_ty = p_ty.add_run()
    r_ty.text = "Thank You!"
    r_ty.font.size = Pt(32)
    r_ty.font.bold = True
    r_ty.font.color.rgb = CYAN
    
    p_ty2 = tb_ty.text_frame.add_paragraph()
    p_ty2.alignment = PP_ALIGN.CENTER
    r_ty2 = p_ty2.add_run()
    r_ty2.text = "Questions & Jury Defense"
    r_ty2.font.size = Pt(15)
    r_ty2.font.color.rgb = WHITE
    
    # Inner author badge
    add_rounded_box(slide, Inches(8.4), Inches(3.6), Inches(3.833), Inches(2.7), fill_color=RGBColor(0x0C, 0x15, 0x2A), line_color=RGBColor(0x1B, 0x33, 0x5A), line_width=Pt(1))
    tb_st = slide.shapes.add_textbox(Inches(8.55), Inches(3.75), Inches(3.5), Inches(2.4))
    tf_st = tb_st.text_frame
    
    r_s1 = tf_st.paragraphs[0].add_run()
    r_s1.text = "STUDENT PRESENTER:"
    r_s1.font.size = Pt(10)
    r_s1.font.bold = True
    r_s1.font.color.rgb = CYAN
    
    p_s2 = tf_st.add_paragraph()
    r_s2 = p_s2.add_run()
    r_s2.text = STUDENT_NAME
    r_s2.font.size = Pt(16)
    r_s2.font.bold = True
    r_s2.font.color.rgb = WHITE
    
    p_s3 = tf_st.add_paragraph()
    r_s3 = p_s3.add_run()
    r_s3.text = f"USN: {STUDENT_USN}"
    r_s3.font.size = Pt(12)
    r_s3.font.bold = True
    r_s3.font.color.rgb = GOLD
    
    p_s4 = tf_st.add_paragraph()
    r_s4 = p_s4.add_run()
    r_s4.text = f"{PROGRAM_NAME}\n{COLLEGE_NAME}"
    r_s4.font.size = Pt(10.5)
    r_s4.font.color.rgb = MUTED

    add_slide_footer(slide, 11)

def main():
    prs = Presentation()
    prs.slide_width  = W
    prs.slide_height = H
    
    print("Building Simple 11-Slide Project Expo Presentation...")
    slide_01(prs)
    slide_02(prs)
    slide_03(prs)
    slide_04(prs)
    slide_05(prs)
    slide_06(prs)
    slide_07(prs)
    slide_08(prs)
    slide_09(prs)
    slide_10(prs)
    slide_11(prs)
    
    out_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(out_dir, "CTI_Simple_Expo_Presentation.pptx")
    prs.save(out_path)
    print(f"[SUCCESS] Simple 11-Slide Presentation saved to: {out_path}")

if __name__ == "__main__":
    main()
