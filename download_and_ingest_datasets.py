#!/usr/bin/env python3
"""
Standalone Script: Download, Setup, and Ingest Threat Intelligence Datasets into the CTI Pipeline.
Populates:
- NVD CVE (~25,000+ records)
- MITRE ATT&CK Framework
- Security News Articles
- Phishing Emails
- IOC Records (50,000+ IPs, Domains, Hashes, URLs)
- Malware Technical Reports
"""

import sys
import os
import json

# Add src to python path
SRC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
sys.path.append(SRC_DIR)

from utils.dataset_loader import dataset_manager, preprocess_text
from models.ner_extractor import CTINERExtractor
from models.attack_tagger import AttackTagger
from models.relation_extractor import CTIRelationExtractor
from kg.knowledge_graph import CTIKnowledgeGraph


def run_dataset_pipeline(quick_mode: bool = False, limit_ingest: int = 50):
    print("=" * 65)
    print(" CTI Threat Intelligence Dataset Download & Ingestion Pipeline")
    print("=" * 65)

    # Step 1: Initialize all datasets
    print("\n[Step 1/4] Initializing and preparing all 6 datasets...")
    status = dataset_manager.initialize_all_datasets(quick_mode=quick_mode)

    print("\n[Dataset Summary]")
    for name, info in status.items():
        print(f"  • {name:<16}: {info['file_count']} file(s) ({info['size_mb']} MB) in {info['directory']}")

    # Step 2: Initialize NLP & Analysis Models
    print("\n[Step 2/4] Initializing CTI Analysis Models...")
    ner_extractor = CTINERExtractor()
    attack_tagger = AttackTagger()
    relation_extractor = CTIRelationExtractor()
    kg = CTIKnowledgeGraph()

    # Step 3: Stream and ingest report datasets into Knowledge Graph
    print(f"\n[Step 3/4] Ingesting reports into Knowledge Graph (Limit: {limit_ingest} reports per dataset)...")
    processed_count = 0

    for item in dataset_manager.stream_all_reports(limit_per_dataset=limit_ingest):
        report_id = item["id"]
        raw_text = item["text"]
        text = preprocess_text(raw_text)

        entities = ner_extractor.extract_all_entities(text)
        attack_tags = attack_tagger.tag_report(text)
        relations = relation_extractor.extract_all_relations(text, entities)

        kg.add_entities_from_ner(entities)
        kg.add_entities_from_attack_tags(attack_tags)
        kg.add_relations_from_extraction(relations)

        processed_count += 1
        if processed_count % 10 == 0:
            print(f"  Processed {processed_count} CTI reports...")

    # Step 4: Export Knowledge Graph and Save Statistics
    print("\n[Step 4/4] Saving Knowledge Graph and compiling analytics...")
    output_kg_path = os.path.join(dataset_manager.data_dir, "knowledge_graph.json")
    
    kg_data = kg.export_d3()
    with open(output_kg_path, "w", encoding="utf-8") as f:
        json.dump(kg_data, f, indent=2)

    stats = kg.get_statistics()
    print("\n" + "=" * 65)
    print(" INGESTION COMPLETE - KNOWLEDGE GRAPH STATISTICS")
    print("=" * 65)
    print(f"  Total Nodes           : {stats.get('nodes', 0):,}")
    print(f"  Total Relationships   : {stats.get('edges', 0):,}")
    entity_types = stats.get('entity_types', [])
    print(f"  Entity Types Tracked  : {len(entity_types)}")
    for etype in entity_types:
        nodes_of_type = len(kg.get_entities_by_type(etype))
        print(f"    - {etype:<20}: {nodes_of_type:,} nodes")
    print(f"  Knowledge Graph Saved : {output_kg_path}")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    quick = "--quick" in sys.argv or "-q" in sys.argv
    limit = 20 if quick else 100
    run_dataset_pipeline(quick_mode=quick, limit_ingest=limit)
