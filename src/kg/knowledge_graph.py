import networkx as nx

class CTIKnowledgeGraph:
    def __init__(self):
        self.graph = nx.DiGraph()
        
    def clear(self):
        self.graph.clear()
    
    def add_entities_from_ner(self, entities):
        for entity_type, values in entities.items():
            for value in values:
                self.graph.add_node(value, type=entity_type, value=value)
                
    def add_entities_from_attack_tags(self, attack_tags):
        for tech_id, tech_name in attack_tags.get('techniques', {}).items():
            self.graph.add_node(tech_id, type='attack_technique', name=tech_name)
        for tactic_id, tactic_name in attack_tags.get('tactics', {}).items():
            self.graph.add_node(tactic_id, type='attack_tactic', name=tactic_name)
            
    def add_relations_from_extraction(self, relations):
        for rel in relations:
            # Add nodes if they don't exist yet
            if rel['source'] not in self.graph:
                self.graph.add_node(rel['source'], type='unknown', value=rel['source'])
            if rel['target'] not in self.graph:
                self.graph.add_node(rel['target'], type='unknown', value=rel['target'])
            
            self.graph.add_edge(rel['source'], rel['target'], relation=rel['relation'], confidence=rel['confidence'])
            
    def get_statistics(self):
        entity_types = set(nx.get_node_attributes(self.graph, 'type').values())
        return {
            'nodes': self.graph.number_of_nodes(),
            'edges': self.graph.number_of_edges(),
            'entity_types': list(entity_types)
        }
        
    def get_entities_by_type(self, entity_type):
        return [(n, attr) for n, attr in self.graph.nodes(data=True) if attr.get('type') == entity_type]
        
    def get_entity_neighbors(self, entity_id):
        neighbors = []
        if entity_id in self.graph:
            for neighbor in self.graph.successors(entity_id):
                edge_data = self.graph.get_edge_data(entity_id, neighbor)
                relation_type = edge_data.get('relation', 'unknown')
                attrs = self.graph.nodes[neighbor]
                neighbors.append((neighbor, relation_type, attrs))
        return neighbors
        
    def export_d3(self):
        nodes = []
        for n, attr in self.graph.nodes(data=True):
            group_mapping = {
                'threat_actor': 'ThreatActor',
                'malware': 'Malware'
            }
            g = group_mapping.get(attr.get('type'), 'Other')
            nodes.append({"id": str(n), "group": g})
            
        links = []
        for u, v, d in self.graph.edges(data=True):
            links.append({"source": str(u), "target": str(v), "name": d.get('relation', 'unknown')})
            
        return {"nodes": nodes, "links": links}
