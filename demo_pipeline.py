"""
Demo script showing the full CTI pipeline functionality
"""
import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from utils.data_loader import preprocess_text


def demo_text_preprocessing():
    """Demonstrate text preprocessing functionality"""
    print("=== Text Preprocessing Demo ===")
    
    sample_texts = [
        "  This is a SAMPLE CTI Report  ",
        "Multiple   Spaces   Between   Words",
        "MIXED case TeXt WiTh UPPERCASE"
    ]
    
    for text in sample_texts:
        processed = preprocess_text(text)
        print(f"Original: '{text}'")
        print(f"Processed: '{processed}'")
        print()


def demo_entity_extraction():
    """Demonstrate entity extraction concepts"""
    print("=== Entity Extraction Concepts ===")
    
    # This is a conceptual demo since we don't have all dependencies installed
    print("In a full implementation, the NER extractor would identify:")
    print("- IP addresses (e.g., 192.168.1.100)")
    print("- Domain names (e.g., malware-c2.com)")
    print("- Email addresses (e.g., security@company.com)")
    print("- Hash values (MD5, SHA1, SHA256)")
    print("- CVE identifiers (e.g., CVE-2023-12345)")
    print("- Malware names (e.g., Emotet, TrickBot)")
    print("- Threat actors (e.g., APT29, Lazarus Group)")
    print()


def demo_attack_tagging():
    """Demonstrate ATT&CK tagging concepts"""
    print("=== MITRE ATT&CK Tagging Concepts ===")
    
    print("In a full implementation, the ATT&CK tagger would identify:")
    print("- Techniques: T1059 (Command and Scripting Interpreter)")
    print("- Techniques: T1566 (Phishing)")
    print("- Techniques: T1071 (Application Layer Protocol)")
    print("- Tactics: TA0001 (Initial Access)")
    print("- Tactics: TA0011 (Command and Control)")
    print()


def demo_relation_extraction():
    """Demonstrate relation extraction concepts"""
    print("=== Relation Extraction Concepts ===")
    
    print("In a full implementation, the relation extractor would identify:")
    print("- 'APT29' uses 'Backdoor.X'")
    print("- 'Backdoor.X' communicates_with '192.168.1.100'")
    print("- 'APT29' targets 'Energy Sector'")
    print("- 'Malware.Y' exploits 'CVE-2023-12345'")
    print()


def demo_knowledge_graph():
    """Demonstrate knowledge graph concepts"""
    print("=== Knowledge Graph Concepts ===")
    
    print("In a full implementation, the knowledge graph would contain:")
    print("- Nodes: Threat actors, malware, IPs, domains, CVEs")
    print("- Edges: Relationships with confidence scores")
    print("- Query capabilities: Find all malware used by APT29")
    print("- Query capabilities: Find all IPs communicating with a domain")
    print("- Visualization: Graph representation of threat intelligence")
    print()


def main():
    """Main demo function"""
    print("CTI Analysis Pipeline - Conceptual Demo")
    print("=" * 50)
    print()
    
    demo_text_preprocessing()
    demo_entity_extraction()
    demo_attack_tagging()
    demo_relation_extraction()
    demo_knowledge_graph()
    
    print("=== Pipeline Benefits ===")
    print("1. Automated extraction of threat indicators")
    print("2. Mapping to standardized frameworks (MITRE ATT&CK)")
    print("3. Structured representation of threat intelligence")
    print("4. Enabling automated threat hunting and analysis")
    print("5. Reducing manual analysis time")
    print("6. Improving consistency and accuracy")
    print()
    
    print("To run the full pipeline, install all dependencies:")
    print("1. pip install -r requirements.txt")
    print("2. python -m spacy download en_core_web_sm")
    print("3. python src/main.py --mode demo")
    print()


if __name__ == "__main__":
    main()