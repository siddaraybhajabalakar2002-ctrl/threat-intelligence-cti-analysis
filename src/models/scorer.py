class ThreatScorer:
    def __init__(self):
        # Weights for different entity types
        self.entity_weights = {
            'threat_actor': 15,
            'malware': 10,
            'cve': 10,
            'ip_address': 5,
            'domain': 5,
            'hash_sha256': 2,
            'hash_md5': 2,
            'hash_sha1': 2,
            'registry_key': 3,
            'scheduled_task': 3
        }
        
        # Weights for MITRE Tactics (higher for actual impact/exfil)
        self.tactic_weights = {
            'TA0010': 20, # Exfiltration
            'TA0040': 20, # Impact
            'TA0011': 15, # Command and Control
            'TA0006': 15, # Credential Access
            'TA0008': 10, # Lateral Movement
            'TA0005': 10, # Defense Evasion
            'TA0003': 8,  # Persistence
            'TA0004': 8,  # Privilege Escalation
            'TA0002': 5,  # Execution
            'TA0001': 5,  # Initial Access
            'TA0009': 5,  # Collection
            'TA0007': 5,  # Discovery
        }

    def calculate_severity(self, entities, attack_tags):
        score = 0
        
        # 1. Score based on Entities
        for entity_type, items in entities.items():
            if entity_type in self.entity_weights:
                # Add base weight for the presence of the type + small bonus for multiple
                weight = self.entity_weights[entity_type]
                score += weight + (len(items) * (weight * 0.1))
                
        # 2. Score based on MITRE Tactics
        tactics = attack_tags.get('tactics', {})
        for tactic_id in tactics.keys():
            if tactic_id in self.tactic_weights:
                score += self.tactic_weights[tactic_id]
                
        # 3. Normalize score to 0-10 scale
        capped_score = min(score, 100)
        final_score = round(capped_score / 10.0, 1)
        
        # 4. Determine Severity Level
        level = "LOW"
        if final_score >= 8.0:
            level = "CRITICAL"
        elif final_score >= 6.0:
            level = "HIGH"
        elif final_score >= 3.5:
            level = "MEDIUM"
            
        return {
            "score": final_score,
            "level": level
        }
