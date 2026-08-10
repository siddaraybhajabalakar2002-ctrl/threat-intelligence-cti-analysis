import argparse
import sys
import os

# Add the project root to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

def main():
    parser = argparse.ArgumentParser(description="CTI Analysis Pipeline")
    parser.add_argument("--mode", choices=["demo", "api", "process", "datasets"], required=True,
                        help="Run mode: demo, api, process, or datasets")
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
            
        # Quick processing logic for the process mode
        from utils.data_loader import preprocess_text
        from models.ner_extractor import CTINERExtractor
        from models.attack_tagger import AttackTagger
        
        processed_text = preprocess_text(text)
        ner = CTINERExtractor()
        tagger = AttackTagger()
        
        print("\n--- Entities Found ---")
        entities = ner.extract_all_entities(processed_text)
        import json
        print(json.dumps(entities, indent=2))
        
        print("\n--- ATT&CK Tags ---")
        tags = tagger.tag_report(processed_text)
        print(json.dumps(tags, indent=2))
        
if __name__ == "__main__":
    main()
