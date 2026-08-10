"""
Usage example for the CTI Analysis Pipeline
"""
import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from pipelines.cti_pipeline import CTIPipeline


def main():
    """Demonstrate how to use the CTI pipeline"""
    print("CTI Analysis Pipeline Usage Example")
    print("=" * 40)
    
    # Initialize the pipeline
    print("1. Initializing CTI Pipeline...")
    pipeline = CTIPipeline()
    print("   Pipeline initialized successfully!")
    print()
    
    # Example 1: Process a single CTI report
    print("2. Processing a Single CTI Report...")
    sample_report = """
    APT29 has been observed using a new backdoor called "Trojan.HiddenAdapter" 
    in their recent campaign targeting the energy sector. The malware connects 
    to command and control servers at 192.168.1.100 and c2.hiddenadapter.com. 
    The attack exploits CVE-2023-12345 and uses T1059 (Command-Line Interface) 
    and T1078 (Valid Accounts) techniques. Security researchers at 
    security@cybersec.com have analyzed the samples.
    """
    
    # Process the report
    results = pipeline.process_report(sample_report, "example_report_001")
    
    print(f"   Report ID: {results['report_id']}")
    print(f"   Entities found: {sum(len(v) for v in results['entities'].values())}")
    print(f"   Techniques identified: {len(results['attack_tags']['techniques'])}")
    print(f"   Relations extracted: {len(results['relations'])}")
    print()
    
    # Example 2: Query the knowledge graph
    print("3. Querying the Knowledge Graph...")
    
    # Query for threat actors (note: lowercase)
    actors_result = pipeline.query_knowledge_graph('entity_type', 'threat_actor')
    print(f"   Threat actors in knowledge graph: {len(actors_result['results'])}")
    
    # Query for neighbors of apt29 (note: lowercase)
    neighbors_result = pipeline.query_knowledge_graph('entity_neighbors', 'apt29')
    print(f"   Relationships for apt29: {len(neighbors_result['results'])}")
    
    # Query for ATT&CK techniques
    techniques_result = pipeline.query_knowledge_graph('entity_type', 'attack_technique')
    print(f"   ATT&CK techniques in knowledge graph: {len(techniques_result['results'])}")
    print()
    
    # Example 3: Get threat intelligence brief
    print("4. Generating Threat Intelligence Brief...")
    brief = pipeline.get_threat_intel_brief()
    print(f"   Graph nodes: {brief['graph_statistics']['nodes']}")
    print(f"   Graph edges: {brief['graph_statistics']['edges']}")
    print(f"   Entity types: {len(brief['entity_type_distribution'])}")
    print()
    
    # Example 4: Get threat actor summary (note: lowercase)
    print("5. Getting Threat Actor Summary...")
    actor_summary = pipeline.get_threat_actor_summary("apt29")
    if "error" not in actor_summary:
        print(f"   Actor: {actor_summary['actor_name']}")
        print(f"   Related entities: {len(actor_summary['related_entities'])}")
    else:
        print(f"   Error: {actor_summary['error']}")
    print()
    
    # Example 5: Process multiple reports
    print("6. Processing Multiple Reports...")
    reports = [
        "APT29 uses Trojan.HiddenAdapter malware and targets energy sector.",
        "The malware communicates with C2 at 192.168.1.100 and uses T1059 technique."
    ]
    report_ids = ["report_001", "report_002"]
    
    batch_results = pipeline.process_reports(reports, report_ids)
    print(f"   Processed {len(batch_results)} reports")
    print(f"   Total entities: {sum(sum(len(v) for v in r['entities'].values()) for r in batch_results)}")
    print()
    
    print("Usage example completed successfully!")
    print()
    print("Next steps:")
    print("1. Try processing your own CTI reports")
    print("2. Explore the API endpoints for integration")
    print("3. Extend the pipeline with custom entity types")
    print("4. Add machine learning models for improved accuracy")


if __name__ == "__main__":
    main()