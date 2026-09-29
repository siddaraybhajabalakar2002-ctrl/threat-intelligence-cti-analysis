import argparse
import sys
import os
import unittest

# Add the project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
sys.path.append(SRC_DIR)

def main():
    parser = argparse.ArgumentParser(description="CTI Analysis Pipeline")
    parser.add_argument("--mode", choices=["demo", "api", "process", "datasets", "test"], required=True,
                        help="Run mode: demo, api, process, datasets, or test")
    parser.add_argument("--input", type=str, help="Input file path for process mode")
    
    args = parser.parse_args()
    
    if args.mode == "api":
        # Import and start the Flask API
        from api.app import start_server
        start_server()
        
    elif args.mode == "demo":
        # Run the complete demo script
        import complete_demo
        complete_demo.complete_demo()
        
    elif args.mode == "datasets":
        # Run dataset setup and ingestion
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        import download_and_ingest_datasets
        download_and_ingest_datasets.run_dataset_pipeline()

    elif args.mode == "test":
        print("Running all CTI Analysis Pipeline unit tests...")
        loader = unittest.TestLoader()
        suite = loader.discover(start_dir=PROJECT_ROOT, pattern="test_*.py")
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        sys.exit(0 if result.wasSuccessful() else 1)
        
    elif args.mode == "process":
        if not args.input:
            print("Error: --input is required for process mode.")
            sys.exit(1)
            
        print(f"Processing file: {args.input}")
        try:
            with open(args.input, 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception as e:
            print(f"Failed to read file: {e}")
            sys.exit(1)
            
        # Processing logic for process mode
        from utils.data_loader import preprocess_text
        from models.ner_extractor import CTINERExtractor
        from models.attack_tagger import AttackTagger
        from models.relation_extractor import CTIRelationExtractor
        from models.scorer import ThreatScorer
        from models.recommendation_engine import RecommendationEngine
        
        processed_text = preprocess_text(text)
        ner = CTINERExtractor()
        tagger = AttackTagger()
        relation_extractor = CTIRelationExtractor()
        scorer = ThreatScorer()
        rec_engine = RecommendationEngine()
        
        print("\n--- Entities Found ---")
        entities = ner.extract_all_entities(processed_text)
        import json
        print(json.dumps(entities, indent=2))
        
        print("\n--- ATT&CK Tags ---")
        tags = tagger.tag_report(processed_text)
        print(json.dumps(tags, indent=2))

        print("\n--- Threat Relations ---")
        relations = relation_extractor.extract_all_relations(processed_text, entities)
        print(json.dumps(relations, indent=2))

        print("\n--- Severity Score ---")
        severity = scorer.calculate_severity(entities, tags)
        print(json.dumps(severity, indent=2))

        print("\n--- Recommendations ---")
        recs = rec_engine.generate_recommendations(entities, tags, severity)
        print(json.dumps(recs, indent=2))
        
if __name__ == "__main__":
    main()
