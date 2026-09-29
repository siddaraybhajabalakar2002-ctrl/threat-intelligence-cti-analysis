import json
import os
import networkx as nx
from typing import Dict, Any, List

class CTIKnowledgeGraph:
    def __init__(self):
        self.graph = nx.DiGraph()
        
    def clear(self):
        self.graph.clear()
    
    def add_entities_from_ner(self, entities: Dict[str, List[str]]):
        for entity_type, values in entities.items():
            for value in values:
                self.graph.add_node(str(value), type=entity_type, value=str(value))
                
    def add_entities_from_attack_tags(self, attack_tags: Dict[str, Dict[str, str]]):
        for tech_id, tech_name in attack_tags.get('techniques', {}).items():
            self.graph.add_node(str(tech_id), type='attack_technique', name=str(tech_name), value=str(tech_id))
        for tactic_id, tactic_name in attack_tags.get('tactics', {}).items():
            self.graph.add_node(str(tactic_id), type='attack_tactic', name=str(tactic_name), value=str(tactic_id))
            
    def add_relations_from_extraction(self, relations: List[Dict[str, Any]]):
        for rel in relations:
            src = str(rel['source'])
            tgt = str(rel['target'])
            relation = rel.get('relation', 'related_to')
            confidence = rel.get('confidence', 0.8)

            # Add nodes if they don't exist yet
            if src not in self.graph:
                self.graph.add_node(src, type='entity', value=src)
            if tgt not in self.graph:
                self.graph.add_node(tgt, type='entity', value=tgt)
            
            self.graph.add_edge(src, tgt, relation=relation, confidence=confidence)
            
    def get_statistics(self) -> Dict[str, Any]:
        entity_types = set(nx.get_node_attributes(self.graph, 'type').values())
        return {
            'nodes': self.graph.number_of_nodes(),
            'edges': self.graph.number_of_edges(),
            'entity_types': list(entity_types)
        }
        
    def get_entities_by_type(self, entity_type: str) -> List[tuple]:
        return [(n, attr) for n, attr in self.graph.nodes(data=True) if attr.get('type') == entity_type]
        
    def get_entity_neighbors(self, entity_id: str) -> List[tuple]:
        neighbors = []
        if entity_id in self.graph:
            for neighbor in self.graph.successors(entity_id):
                edge_data = self.graph.get_edge_data(entity_id, neighbor)
                relation_type = edge_data.get('relation', 'unknown')
                attrs = self.graph.nodes[neighbor]
                neighbors.append((neighbor, relation_type, attrs))
        return neighbors
        
    def export_d3(self) -> Dict[str, Any]:
        group_mapping = {
            'threat_actor': 'ThreatActor',
            'malware': 'Malware',
            'ip_address': 'IPAddress',
            'ip': 'IPAddress',
            'domain': 'Domain',
            'url': 'URL',
            'cve': 'CVE',
            'attack_technique': 'Technique',
            'attack_tactic': 'Tactic',
            'hash_sha256': 'Hash',
            'hash_md5': 'Hash',
            'hash_sha1': 'Hash',
            'registry_key': 'Persistence',
            'scheduled_task': 'Persistence',
            'target': 'Target'
        }

        nodes = []
        for n, attr in self.graph.nodes(data=True):
            raw_type = attr.get('type', 'Other')
            g = group_mapping.get(raw_type, 'Other')
            label = attr.get('name') or attr.get('value') or str(n)
            nodes.append({
                "id": str(n),
                "name": str(label),
                "group": g,
                "type": raw_type
            })
            
        links = []
        for u, v, d in self.graph.edges(data=True):
            links.append({
                "source": str(u),
                "target": str(v),
                "name": d.get('relation', 'related_to'),
                "confidence": d.get('confidence', 0.8)
            })
            
        return {"nodes": nodes, "links": links}

    def save_to_json(self, filepath: str):
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        data = self.export_d3()
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def load_from_json(self, filepath: str):
        if not os.path.exists(filepath):
            return
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for node in data.get('nodes', []):
            self.graph.add_node(node['id'], type=node.get('type', 'Other'), name=node.get('name', node['id']))
        for link in data.get('links', []):
            self.graph.add_edge(link['source'], link['target'], relation=link.get('name', 'related_to'), confidence=link.get('confidence', 0.8))
