"""
Complete demonstration of the CTI Analysis Pipeline
"""
import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from utils.data_loader import preprocess_text
from models.ner_extractor import CTINERExtractor
from models.attack_tagger import AttackTagger
from models.relation_extractor import CTIRelationExtractor
from kg.knowledge_graph import CTIKnowledgeGraph


def complete_demo():
    """Demonstrate the complete CTI pipeline workflow"""
    print("Complete CTI Analysis Pipeline Demonstration")
    print("=" * 50)
    
    # Sample CTI report
    cti_report = r"""
    CYBER THREAT REPORT: APT29 CAMPAIGN ANALYSIS

    Executive Summary:
    APT29 (also known as Cozy Bear) has been conducting a sophisticated cyber espionage campaign 
    targeting government institutions in North America and Europe. The campaign, which began in 
    early 2023, leverages a previously unknown backdoor malware called "SilentHorn" and exploits 
    a zero-day vulnerability in Microsoft Exchange Server (CVE-2023-45678).

    Technical Details:
    The initial compromise occurs through spear-phishing emails containing malicious Office documents. 
    Once executed, the documents deploy SilentHorn, which establishes persistence through Windows 
    Registry modifications and creates a hidden scheduled task named "WindowsUpdateTask".

    SilentHorn communicates with command and control infrastructure hosted on 185.132.189.10 and 
    backup C2 at 91.243.250.21. The malware uses DNS tunneling for data exfiltration and has been 
    observed targeting files with extensions .doc, .pdf, .xls, and .ppt.

    The threat actor employs advanced evasion techniques, including process hollowing and direct 
    system calls to avoid detection by security software. Network traffic is encrypted using a 
    custom implementation of AES-256.

    Indicators of Compromise:
    - SHA256: 5f3a8c9b2d4e6f1a0c5e8d3b7f9a1c4e6d8f2a5b9c3e7d1a4f6b8c2e0a5d9f3c (SilentHorn payload)
    - SHA256: a1b2c3d4e5f67890123456789012345678901234567890123456789012345678 (C2 communication module)
    - IP Addresses: 185.132.189.10, 91.243.250.21
    - Domain: silentc2[.]net, backup-c2[.]org
    - Registry Key: HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run\WindowsUpdateTask
    - Scheduled Task: WindowsUpdateTask

    MITRE ATT&CK Mapping:
    - Initial Access: T1566 (Phishing), T1190 (Exploit Public-Facing Application)
    - Execution: T1204 (User Execution), T1059 (Command and Scripting Interpreter)
    - Persistence: T1547 (Registry Run Keys / Startup Folder), T1053 (Scheduled Task/Job)
    - Defense Evasion: T1036 (Masquerading), T1055 (Process Injection)
    - Command and Control: T1071 (Application Layer Protocol), T1041 (Exfiltration Over C2 Channel)
    - Exfiltration: T1041 (Exfiltration Over C2 Channel), T1071 (Application Layer Protocol)

    Recommendations:
    1. Apply the latest Microsoft security updates immediately
    2. Block network communication to the identified IP addresses and domains
    3. Scan systems for the specified file hashes
    4. Monitor for the creation of the WindowsUpdateTask scheduled task
    5. Implement enhanced DNS monitoring to detect tunneling activity

    This campaign demonstrates APT29's continued evolution and capability to develop and deploy 
    sophisticated malware for long-term espionage operations.
    """
    
    print("Processing CTI Report...")
    print(f"Report length: {len(cti_report)} characters")
    print()
    
    # Step 1: Text Preprocessing
    print("Step 1: Text Preprocessing")
    processed_text = preprocess_text(cti_report)
    print(f"Processed text length: {len(processed_text)} characters")
    print()
    
    # Step 2: Named Entity Recognition
    print("Step 2: Named Entity Recognition")
    ner_extractor = CTINERExtractor()
    entities = ner_extractor.extract_all_entities(processed_text)
    print(f"Entities extracted: {len(entities)} types")
    for entity_type, values in entities.items():
        print(f"  {entity_type}: {len(values)} found")
        if values:
            print(f"    Examples: {values[:3]}")
    print()
    
    # Step 3: ATT&CK Technique Tagging
    print("Step 3: MITRE ATT&CK Technique Tagging")
    attack_tagger = AttackTagger()
    attack_tags = attack_tagger.tag_report(processed_text)
    techniques = attack_tags['techniques']
    tactics = attack_tags['tactics']
    print(f"Techniques identified: {len(techniques)}")
    print(f"Tactics identified: {len(tactics)}")
    
    # Show some techniques
    for tech_id, tech_name in list(techniques.items())[:5]:
        print(f"  {tech_id}: {tech_name}")
    print()
    
    # Step 4: Relation Extraction
    print("Step 4: Relation Extraction")
    relation_extractor = CTIRelationExtractor()
    relations = relation_extractor.extract_all_relations(processed_text)
    print(f"Relations extracted: {len(relations)}")
    for i, rel in enumerate(relations[:5]):
        print(f"  {rel['source']} --[{rel['relation']}]--> {rel['target']} (confidence: {rel['confidence']})")
    print()
    
    # Step 5: Knowledge Graph Construction
    print("Step 5: Knowledge Graph Construction")
    kg = CTIKnowledgeGraph()
    
    # Add entities
    kg.add_entities_from_ner(entities)
    kg.add_entities_from_attack_tags(attack_tags)
    
    # Add relations
    kg.add_relations_from_extraction(relations)
    
    # Show statistics
    stats = kg.get_statistics()
    print(f"Knowledge Graph Statistics:")
    print(f"  Nodes: {stats['nodes']}")
    print(f"  Edges: {stats['edges']}")
    print(f"  Entity Types: {len(stats['entity_types'])}")
    print()
    
    # Show some entities
    print("Sample Entities in Knowledge Graph:")
    threat_actors = kg.get_entities_by_type("threat_actor")
    if threat_actors:
        print(f"  Threat Actors: {len(threat_actors)}")
        for actor_id, attrs in threat_actors[:3]:
            print(f"    {actor_id}: {attrs.get('value', 'N/A')}")
    
    malwares = kg.get_entities_by_type("malware")
    if malwares:
        print(f"  Malware: {len(malwares)}")
        for malware_id, attrs in malwares[:3]:
            print(f"    {malware_id}: {attrs.get('value', 'N/A')}")
    
    techniques_in_kg = kg.get_entities_by_type("attack_technique")
    if techniques_in_kg:
        print(f"  ATT&CK Techniques: {len(techniques_in_kg)}")
        for tech_id, attrs in techniques_in_kg[:3]:
            print(f"    {tech_id}: {attrs.get('name', 'N/A')}")
    print()
    
    # Show relationships for APT29 if it exists
    if "APT29" in kg.graph.nodes:
        neighbors = kg.get_entity_neighbors("APT29")
        print(f"Relationships for APT29: {len(neighbors)}")
        for neighbor_id, relation_type, attrs in neighbors[:5]:
            print(f"  APT29 --[{relation_type}]--> {neighbor_id}")
    print()
    
    # Step 6: Intelligence Summary
    print("Step 6: Intelligence Summary")
    print("KEY FINDINGS:")
    print(f"  Threat Actor: APT29 (Cozy Bear)")
    print(f"  Malware: SilentHorn")
    print(f"  Indicators of Compromise: {sum(len(values) for values in entities.values())}")
    print(f"  ATT&CK Techniques: {len(techniques)}")
    print(f"  ATT&CK Tactics: {len(tactics)}")
    print()
    
    print("RECOMMENDATIONS:")
    print("  1. Block network communication to identified IPs and domains")
    print("  2. Scan systems for specified file hashes")
    print("  3. Monitor for WindowsUpdateTask scheduled task")
    print("  4. Implement enhanced DNS monitoring for tunneling detection")
    print("  5. Apply latest Microsoft security updates")
    print()
    
    print("Pipeline demonstration completed successfully!")


if __name__ == "__main__":
    complete_demo()