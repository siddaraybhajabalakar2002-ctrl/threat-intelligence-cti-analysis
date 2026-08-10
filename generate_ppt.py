from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
import copy
import os

# ── Colour Palette ──────────────────────────────────────────────────────────
DARK_BG     = RGBColor(0x0D, 0x1B, 0x2A)   # deep navy
ACCENT_BLUE = RGBColor(0x00, 0x78, 0xD4)   # Microsoft-style blue
ACCENT_CYAN = RGBColor(0x00, 0xBC, 0xF2)   # bright cyan
WHITE       = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT_GRAY  = RGBColor(0xD9, 0xE8, 0xF5)
GOLD        = RGBColor(0xFF, 0xC0, 0x0D)

W = Inches(13.333)   # widescreen 16:9 width
H = Inches(7.5)      # widescreen 16:9 height

# ── Helpers ──────────────────────────────────────────────────────────────────

def set_slide_bg(slide, color: RGBColor):
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_rect(slide, left, top, width, height, fill_color=None, line_color=None, line_width=Pt(0)):
    from pptx.util import Pt
    shape = slide.shapes.add_shape(1, left, top, width, height)   # MSO_SHAPE_TYPE.RECTANGLE = 1
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


def add_text_box(slide, text, left, top, width, height,
                 font_size=18, bold=False, color=WHITE,
                 align=PP_ALIGN.LEFT, wrap=True):
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = wrap
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run.font.color.rgb = color
    return txBox


def add_title_bar(slide, title_text, sub_text=None):
    """Dark navy title bar at top of slide."""
    bar = add_rect(slide, Inches(0), Inches(0), W, Inches(1.4), fill_color=DARK_BG)
    add_text_box(slide, title_text,
                 Inches(0.4), Inches(0.12), Inches(10), Inches(0.7),
                 font_size=28, bold=True, color=ACCENT_CYAN, align=PP_ALIGN.LEFT)
    if sub_text:
        add_text_box(slide, sub_text,
                     Inches(0.4), Inches(0.78), Inches(10), Inches(0.5),
                     font_size=14, bold=False, color=LIGHT_GRAY, align=PP_ALIGN.LEFT)
    # accent line
    add_rect(slide, Inches(0), Inches(1.4), W, Inches(0.05), fill_color=ACCENT_BLUE)


def add_bullet_points(slide, bullets, left, top, width, height,
                      bullet_font_size=15, color=WHITE, number=False):
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    first = True
    for i, bullet in enumerate(bullets):
        if first:
            p = tf.paragraphs[0]
            first = False
        else:
            p = tf.add_paragraph()
        p.space_before = Pt(6)
        run = p.add_run()
        prefix = f"{i+1}. " if number else "▸  "
        run.text = prefix + bullet
        run.font.size = Pt(bullet_font_size)
        run.font.color.rgb = color


def footer(slide, name, regno):
    add_rect(slide, Inches(0), Inches(7.1), W, Inches(0.4), fill_color=DARK_BG)
    add_text_box(slide, f"{name}  |  Reg No: {regno}",
                 Inches(0.3), Inches(7.13), Inches(10), Inches(0.35),
                 font_size=10, color=LIGHT_GRAY)


# ── Slide Builders ───────────────────────────────────────────────────────────

def slide1_title(prs, name, regno):
    slide = prs.slides.add_slide(prs.slide_layouts[6])   # blank
    set_slide_bg(slide, DARK_BG)

    # decorative left bar
    add_rect(slide, Inches(0), Inches(0), Inches(0.18), H, fill_color=ACCENT_BLUE)
    add_rect(slide, Inches(0.18), Inches(0), Inches(0.06), H, fill_color=ACCENT_CYAN)

    # big title
    add_text_box(slide, "Cyber Threat Intelligence",
                 Inches(0.5), Inches(1.0), Inches(12.5), Inches(1.2),
                 font_size=36, bold=True, color=ACCENT_CYAN, align=PP_ALIGN.LEFT)
    add_text_box(slide, "Using Pipeline, NLP and LLM",
                 Inches(0.5), Inches(2.0), Inches(12.5), Inches(1.0),
                 font_size=32, bold=True, color=WHITE, align=PP_ALIGN.LEFT)

    # gold divider line
    add_rect(slide, Inches(0.5), Inches(3.1), Inches(6), Inches(0.06), fill_color=GOLD)

    # subtitle block
    add_text_box(slide, "A Project Presentation for HOD Approval",
                 Inches(0.5), Inches(3.3), Inches(12), Inches(0.5),
                 font_size=16, color=LIGHT_GRAY)

    # name / regno box
    add_rect(slide, Inches(0.5), Inches(4.4), Inches(6), Inches(1.6),
             fill_color=RGBColor(0x13, 0x2A, 0x45), line_color=ACCENT_BLUE, line_width=Pt(1.5))
    add_text_box(slide, f"Presented by:  {name}",
                 Inches(0.7), Inches(4.6), Inches(5.5), Inches(0.5),
                 font_size=15, bold=True, color=WHITE)
    add_text_box(slide, f"Reg No:  {regno}",
                 Inches(0.7), Inches(5.0), Inches(5.5), Inches(0.4),
                 font_size=14, color=LIGHT_GRAY)
    add_text_box(slide, "Department of Computer Science",
                 Inches(0.7), Inches(5.35), Inches(5.5), Inches(0.4),
                 font_size=13, color=LIGHT_GRAY)

    # decorative corner accent
    add_rect(slide, Inches(10), Inches(5.5), Inches(3.1), Inches(1.8),
             fill_color=RGBColor(0x00, 0x78, 0xD4))
    add_text_box(slide, "2024–25",
                 Inches(10.2), Inches(5.8), Inches(2.5), Inches(0.8),
                 font_size=28, bold=True, color=WHITE, align=PP_ALIGN.CENTER)


def slide2_introduction(prs, name, regno):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, RGBColor(0xF0, 0xF5, 0xFB))
    add_title_bar(slide, "Introduction", "Understanding Cyber Threat Intelligence (CTI)")

    boxes = [
        ("What is CTI?",
         "Cyber Threat Intelligence (CTI) is structured, actionable information about cyber threats that helps organisations anticipate, prevent, and respond to attacks."),
        ("Data Sources",
         "CTI comes from incident reports, security blogs, MISP feeds, malware advisories, and the MITRE ATT&CK knowledge base — mostly in unstructured text form."),
        ("The Human Bottleneck",
         "Security analysts manually read thousands of pages to extract IOCs and identify attacker behaviour — a slow, error-prone, and unscalable process."),
        ("The Opportunity",
         "NLP and LLM technologies can automate this extraction, classify attacker techniques, and structure intelligence into a queryable Knowledge Graph."),
    ]

    col_w = Inches(5.8)
    col_gap = Inches(0.4)
    for idx, (heading, body) in enumerate(boxes):
        col = idx % 2
        row = idx // 2
        lft = Inches(0.35) + col * (col_w + col_gap)
        tp  = Inches(1.65) + row * Inches(2.5)
        add_rect(slide, lft, tp, col_w, Inches(2.35),
                 fill_color=DARK_BG, line_color=ACCENT_BLUE, line_width=Pt(1))
        add_text_box(slide, heading,
                     lft + Inches(0.15), tp + Inches(0.12), col_w - Inches(0.3), Inches(0.45),
                     font_size=14, bold=True, color=ACCENT_CYAN)
        add_text_box(slide, body,
                     lft + Inches(0.15), tp + Inches(0.55), col_w - Inches(0.3), Inches(1.7),
                     font_size=12, color=WHITE)

    footer(slide, name, regno)


def slide3_problem(prs, name, regno):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, RGBColor(0xF0, 0xF5, 0xFB))
    add_title_bar(slide, "Problem Statement", "Core challenges driving this project")

    problems = [
        ("Unstructured Data Overload",
         "Critical threat intelligence is buried in unstructured text (blogs, advisories, reports). Automated systems cannot act on free-form text directly."),
        ("Massive Manual Effort",
         "Extracting IOCs — IP addresses, file hashes, domain names, CVEs — and identifying threat-actor relationships requires hundreds of analyst hours per week."),
        ("Inconsistent ATT&CK Mapping",
         "Mapping observed attacker behaviour to the MITRE ATT&CK framework is expert-dependent, inconsistent, and prone to human error under pressure."),
        ("Siloed, Disconnected Intelligence",
         "Threat data exists in isolation. Without a structured relationship model, analysts cannot discover hidden links between actors, malware, and vulnerabilities."),
        ("Delayed Threat Response",
         "Manual workflows mean threats are often fully understood only after damage has been done. Speed of intelligence processing directly impacts incident response time."),
    ]

    for idx, (heading, body) in enumerate(problems):
        tp = Inches(1.6) + idx * Inches(1.06)
        add_rect(slide, Inches(0.3), tp, Inches(0.08), Inches(0.85), fill_color=GOLD)
        add_text_box(slide, heading,
                     Inches(0.55), tp + Inches(0.02), Inches(4.0), Inches(0.38),
                     font_size=13, bold=True, color=DARK_BG)
        add_text_box(slide, body,
                     Inches(0.55), tp + Inches(0.40), Inches(12.4), Inches(0.50),
                     font_size=12, color=RGBColor(0x22, 0x22, 0x22))

    footer(slide, name, regno)


def slide4_aim(prs, name, regno):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, DARK_BG)
    add_title_bar(slide, "Aim of the Project", "The overarching goal")

    # central aim statement
    add_rect(slide, Inches(0.5), Inches(1.6), Inches(12.3), Inches(2.2),
             fill_color=RGBColor(0x13, 0x2A, 0x45), line_color=ACCENT_CYAN, line_width=Pt(2))
    add_text_box(slide,
                 "To design and implement an automated, end-to-end Cyber Threat Intelligence "
                 "analysis pipeline that leverages Natural Language Processing (NLP) and Large "
                 "Language Models (LLMs) to ingest unstructured CTI reports, automatically "
                 "extract threat entities and relationships, map them to the MITRE ATT\u0026CK "
                 "framework, and construct a queryable Knowledge Graph — enabling faster, "
                 "more accurate, and consistent threat intelligence for cybersecurity teams.",
                 Inches(0.75), Inches(1.75), Inches(11.8), Inches(1.9),
                 font_size=15, color=WHITE)

    pillars = ["Automation", "Accuracy", "Speed", "Scalability"]
    colors  = [ACCENT_BLUE, ACCENT_CYAN, GOLD, RGBColor(0x6B, 0xD4, 0x5A)]
    for i, (p, c) in enumerate(zip(pillars, colors)):
        lft = Inches(0.5) + i * Inches(3.2)
        add_rect(slide, lft, Inches(4.1), Inches(2.8), Inches(1.0), fill_color=c)
        add_text_box(slide, p, lft, Inches(4.1), Inches(2.8), Inches(1.0),
                     font_size=20, bold=True, color=DARK_BG, align=PP_ALIGN.CENTER)

    footer(slide, name, regno)


def slide5_objectives(prs, name, regno):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, RGBColor(0xF0, 0xF5, 0xFB))
    add_title_bar(slide, "Objectives of the Project", "Six specific, measurable goals")

    objectives = [
        ("01", "Automated IOC Extraction",
         "Develop a regex + NLP Named Entity Recogniser (NER) to extract IPs, domains, file hashes (MD5/SHA1/SHA256), CVEs, registry keys, and scheduled tasks."),
        ("02", "MITRE ATT&CK Classification",
         "Build a tagger that maps free-text descriptions to 100+ ATT&CK Techniques (e.g. T1059) and Tactics (e.g. TA0001 Initial Access) using keyword & semantic analysis."),
        ("03", "Relation Extraction",
         "Identify and extract semantic relationships: Actor→uses→Malware, Malware→communicates_with→IP, Actor→targets→Sector, Malware→exploits→CVE."),
        ("04", "Knowledge Graph Construction",
         "Build a directed, weighted graph (NetworkX) where nodes are entities and edges are labelled relationships with confidence scores for querying and pathfinding."),
        ("05", "Threat Severity Scoring",
         "Calculate a normalised 0–10 severity score based on entity type weights and MITRE Tactic weights (e.g. Exfiltration = 20, Initial Access = 5)."),
        ("06", "RESTful API & LLM Integration",
         "Expose the pipeline via Flask API endpoints (/analyze, /analyze/file, /knowledge_graph/statistics) and integrate LLMs for report summarisation and Q&A."),
    ]

    col_w = Inches(6.0)
    for idx, (num, title, body) in enumerate(objectives):
        col = idx % 2
        row = idx // 2
        lft = Inches(0.25) + col * (col_w + Inches(0.35))
        tp  = Inches(1.6)  + row * Inches(1.92)
        add_rect(slide, lft, tp, col_w, Inches(1.8),
                 fill_color=WHITE, line_color=ACCENT_BLUE, line_width=Pt(1.5))
        # number badge
        add_rect(slide, lft, tp, Inches(0.55), Inches(1.8), fill_color=ACCENT_BLUE)
        add_text_box(slide, num, lft, tp + Inches(0.55), Inches(0.55), Inches(0.65),
                     font_size=15, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        add_text_box(slide, title,
                     lft + Inches(0.65), tp + Inches(0.08), col_w - Inches(0.75), Inches(0.42),
                     font_size=13, bold=True, color=DARK_BG)
        add_text_box(slide, body,
                     lft + Inches(0.65), tp + Inches(0.48), col_w - Inches(0.75), Inches(1.2),
                     font_size=11, color=RGBColor(0x33, 0x33, 0x33))

    footer(slide, name, regno)


def slide6_scope(prs, name, regno):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, DARK_BG)
    add_title_bar(slide, "Scope of the Project", "What is and is not covered")

    # IN SCOPE
    add_rect(slide, Inches(0.3), Inches(1.6), Inches(5.9), Inches(5.3),
             fill_color=RGBColor(0x0A, 0x25, 0x3D), line_color=ACCENT_CYAN, line_width=Pt(1.5))
    add_text_box(slide, "✔  IN SCOPE",
                 Inches(0.5), Inches(1.65), Inches(5.5), Inches(0.45),
                 font_size=15, bold=True, color=ACCENT_CYAN)
    in_scope = [
        "Processing English-language CTI reports (text & PDF)",
        "Extraction of IPs, domains, hashes, CVEs, registry keys, malware names, and threat actors",
        "MITRE ATT&CK Technique & Tactic tagging (100+ techniques)",
        "Relationship extraction between threat entities",
        "Knowledge Graph construction with confidence-scored edges",
        "Threat severity scoring (0–10 scale, 4 levels)",
        "REST API for integration with SIEM/SOC tools",
        "LLM-based summarisation and Q&A interface",
    ]
    add_bullet_points(slide, in_scope, Inches(0.5), Inches(2.2), Inches(5.5), Inches(4.5),
                      bullet_font_size=12, color=WHITE)

    # OUT OF SCOPE
    add_rect(slide, Inches(6.5), Inches(1.6), Inches(6.5), Inches(5.3),
             fill_color=RGBColor(0x2D, 0x0A, 0x0A), line_color=GOLD, line_width=Pt(1.5))
    add_text_box(slide, "✖  OUT OF SCOPE",
                 Inches(6.7), Inches(1.65), Inches(6.0), Inches(0.45),
                 font_size=15, bold=True, color=GOLD)
    out_scope = [
        "Non-English CTI reports",
        "Real-time streaming feed ingestion (future enhancement)",
        "Full LLM fine-tuning on custom datasets",
        "Advanced graph visualisation dashboard",
        "STIX/TAXII protocol integration",
        "Somatic/cancer mutation data (domain specific)",
    ]
    add_bullet_points(slide, out_scope, Inches(6.7), Inches(2.2), Inches(6.1), Inches(4.5),
                      bullet_font_size=12, color=WHITE)

    footer(slide, name, regno)


def slide7_architecture(prs, name, regno):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, RGBColor(0xF0, 0xF5, 0xFB))
    add_title_bar(slide, "System Architecture", "Four-stage automated pipeline")

    stages = [
        (ACCENT_BLUE,   "Stage 1",  "Text Preprocessing\n& NER Extraction",
         "spaCy + Regex\nExtracts IOCs from raw text"),
        (ACCENT_CYAN,   "Stage 2",  "MITRE ATT&CK\nTagger",
         "Keyword + semantic analysis\n100+ techniques mapped"),
        (GOLD,          "Stage 3",  "Knowledge Graph\nConstruction",
         "NetworkX DiGraph\nNodes, edges, confidence scores"),
        (RGBColor(0x6B, 0xD4, 0x5A), "Stage 4", "LLM Interface\n& API Layer",
         "Flask REST API\nLLM summarisation & Q&A"),
    ]

    for i, (color, stage, title, detail) in enumerate(stages):
        lft = Inches(0.3) + i * Inches(3.25)
        add_rect(slide, lft, Inches(1.6), Inches(3.0), Inches(4.6),
                 fill_color=DARK_BG, line_color=color, line_width=Pt(2))
        add_rect(slide, lft, Inches(1.6), Inches(3.0), Inches(0.55), fill_color=color)
        add_text_box(slide, stage, lft, Inches(1.6), Inches(3.0), Inches(0.55),
                     font_size=13, bold=True, color=DARK_BG, align=PP_ALIGN.CENTER)
        add_text_box(slide, title,
                     lft + Inches(0.15), Inches(2.3), Inches(2.7), Inches(0.9),
                     font_size=14, bold=True, color=color)
        add_text_box(slide, detail,
                     lft + Inches(0.15), Inches(3.3), Inches(2.7), Inches(2.7),
                     font_size=12, color=WHITE)

        # arrow between stages
        if i < 3:
            add_text_box(slide, "▶",
                         lft + Inches(3.05), Inches(3.4), Inches(0.2), Inches(0.4),
                         font_size=20, bold=True, color=ACCENT_BLUE, align=PP_ALIGN.CENTER)

    add_text_box(slide,
                 "Input: Raw CTI Report (text / PDF)   →   Output: Entities + ATT&CK Tags + Knowledge Graph + Severity Score",
                 Inches(0.3), Inches(6.4), Inches(12.8), Inches(0.5),
                 font_size=12, bold=True, color=DARK_BG, align=PP_ALIGN.CENTER)

    footer(slide, name, regno)


def slide8_tech_stack(prs, name, regno):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, DARK_BG)
    add_title_bar(slide, "Technology Stack", "Tools and frameworks used in implementation")

    tech = [
        ("Python 3.10+",       "Core implementation language — modules, pipeline orchestration"),
        ("spaCy (en_core_web_sm)", "NLP engine for Named Entity Recognition (ORG, PERSON, PRODUCT)"),
        ("Regular Expressions", "Pattern-based extraction of strict IOC types (IPs, hashes, CVEs)"),
        ("NetworkX",           "Directed graph (DiGraph) for Knowledge Graph construction and traversal"),
        ("Flask",              "Lightweight REST API framework — /analyze, /analyze/file endpoints"),
        ("PyPDF2",             "PDF parsing — extracts text from uploaded CTI report PDFs"),
        ("OpenAI API (optional)", "LLM integration for report summarisation, Q&A, brief generation"),
        ("Docker",             "Containerised deployment for portability and scalability"),
    ]

    for idx, (name_t, desc) in enumerate(tech):
        col = idx % 2
        row = idx // 2
        lft = Inches(0.3) + col * Inches(6.5)
        tp  = Inches(1.6) + row * Inches(1.32)
        add_rect(slide, lft, tp, Inches(6.2), Inches(1.2),
                 fill_color=RGBColor(0x0D, 0x2B, 0x45), line_color=ACCENT_BLUE, line_width=Pt(1))
        add_text_box(slide, name_t,
                     lft + Inches(0.15), tp + Inches(0.08), Inches(5.8), Inches(0.40),
                     font_size=14, bold=True, color=ACCENT_CYAN)
        add_text_box(slide, desc,
                     lft + Inches(0.15), tp + Inches(0.48), Inches(5.8), Inches(0.60),
                     font_size=12, color=LIGHT_GRAY)

    footer(slide, name, regno)


def slide9_value(prs, name, regno):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, RGBColor(0xF0, 0xF5, 0xFB))
    add_title_bar(slide, "Expected Outcomes & Value Proposition", "Why this project matters")

    outcomes = [
        (ACCENT_BLUE, "⚡ Speed",
         "Reduces threat report processing from hours to seconds. Analysts can act on intelligence in near real-time."),
        (ACCENT_CYAN, "🎯 Accuracy",
         "Eliminates manual extraction errors. Regex + NLP achieves consistent, reproducible IOC identification."),
        (GOLD,        "🔗 Connectivity",
         "The Knowledge Graph surfaces hidden relationships — e.g. shared C2 infrastructure between two seemingly unrelated APT groups."),
        (RGBColor(0x6B, 0xD4, 0x5A), "📊 Prioritisation",
         "Automated severity scoring (0–10) helps SOC teams triage thousands of alerts and focus on CRITICAL threats first."),
        (RGBColor(0xFF, 0x66, 0x66), "🔒 Proactive Defence",
         "By mapping behaviour to ATT&CK, defenders can deploy mitigations before an attack reaches its objective."),
        (RGBColor(0xCC, 0x99, 0xFF), "🔌 Integration",
         "The Flask REST API allows plug-and-play integration with any SIEM, SOAR, or threat intelligence platform."),
    ]

    col_w = Inches(4.1)
    for idx, (color, heading, body) in enumerate(outcomes):
        col = idx % 3
        row = idx // 3
        lft = Inches(0.3) + col * (col_w + Inches(0.2))
        tp  = Inches(1.6) + row * Inches(2.6)
        add_rect(slide, lft, tp, col_w, Inches(2.45),
                 fill_color=WHITE, line_color=color, line_width=Pt(2))
        add_rect(slide, lft, tp, col_w, Inches(0.48), fill_color=color)
        add_text_box(slide, heading,
                     lft + Inches(0.1), tp + Inches(0.04), col_w - Inches(0.2), Inches(0.40),
                     font_size=13, bold=True, color=DARK_BG)
        add_text_box(slide, body,
                     lft + Inches(0.1), tp + Inches(0.55), col_w - Inches(0.2), Inches(1.8),
                     font_size=12, color=RGBColor(0x22, 0x22, 0x22))

    footer(slide, name, regno)


def slide10_conclusion(prs, name, regno):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, DARK_BG)

    add_rect(slide, Inches(0), Inches(0), Inches(0.18), H, fill_color=ACCENT_BLUE)
    add_rect(slide, Inches(0.18), Inches(0), Inches(0.06), H, fill_color=ACCENT_CYAN)

    add_text_box(slide, "Conclusion & Request for Approval",
                 Inches(0.5), Inches(0.5), Inches(12.5), Inches(0.9),
                 font_size=30, bold=True, color=ACCENT_CYAN)
    add_rect(slide, Inches(0.5), Inches(1.35), Inches(6.5), Inches(0.06), fill_color=GOLD)

    summary = (
        "The CTI Analysis Pipeline project addresses a critical, real-world problem in "
        "modern cybersecurity. By combining NLP, LLMs, and graph analytics into a single "
        "automated pipeline, this project will:\n\n"
        "▸  Save hundreds of analyst hours per week through automation\n"
        "▸  Improve detection accuracy with consistent, machine-driven IOC extraction\n"
        "▸  Surface hidden threat relationships via a Knowledge Graph\n"
        "▸  Align with industry-standard frameworks (MITRE ATT&CK)\n"
        "▸  Deliver a production-ready REST API for real-world deployment"
    )
    add_text_box(slide, summary,
                 Inches(0.5), Inches(1.6), Inches(9.5), Inches(3.8),
                 font_size=14, color=WHITE)

    add_rect(slide, Inches(0.5), Inches(5.55), Inches(9.5), Inches(1.3),
             fill_color=RGBColor(0x13, 0x2A, 0x45), line_color=ACCENT_CYAN, line_width=Pt(1.5))
    add_text_box(slide, "We respectfully request HOD approval to proceed with this project.",
                 Inches(0.7), Inches(5.65), Inches(9.0), Inches(0.5),
                 font_size=15, bold=True, color=ACCENT_CYAN)
    add_text_box(slide, f"Presented by: {name}   |   Reg No: {regno}",
                 Inches(0.7), Inches(6.1), Inches(9.0), Inches(0.4),
                 font_size=13, color=LIGHT_GRAY)

    add_text_box(slide, "Thank You\n& Questions?",
                 Inches(10.0), Inches(4.0), Inches(3.0), Inches(2.0),
                 font_size=26, bold=True, color=GOLD, align=PP_ALIGN.CENTER)


# ── Main ─────────────────────────────────────────────────────────────────────

def create_presentation():
    NAME   = "Siddaray Bhajabalakar"
    REGNO  = "P03AC24S126056"
    OUTDIR = r"C:\Users\admin\Downloads\threat-intelligence-cti-analysis-main (2)\threat-intelligence-cti-analysis-main"
    OUTFILE = os.path.join(OUTDIR, "CTI_Project_Presentation.pptx")

    prs = Presentation()
    prs.slide_width  = W
    prs.slide_height = H

    slide1_title(prs, NAME, REGNO)
    slide2_introduction(prs, NAME, REGNO)
    slide3_problem(prs, NAME, REGNO)
    slide4_aim(prs, NAME, REGNO)
    slide5_objectives(prs, NAME, REGNO)
    slide6_scope(prs, NAME, REGNO)
    slide7_architecture(prs, NAME, REGNO)
    slide8_tech_stack(prs, NAME, REGNO)
    slide9_value(prs, NAME, REGNO)
    slide10_conclusion(prs, NAME, REGNO)

    prs.save(OUTFILE)
    print(f"Presentation saved to: {OUTFILE}")

if __name__ == '__main__':
    create_presentation()
