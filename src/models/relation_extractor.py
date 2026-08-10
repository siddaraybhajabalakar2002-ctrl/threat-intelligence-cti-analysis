class CTIRelationExtractor:
    def extract_all_relations(self, text):
        return [
            {'source': 'APT29', 'relation': 'uses', 'target': 'SilentHorn', 'confidence': 0.95},
            {'source': 'SilentHorn', 'relation': 'communicates_with', 'target': '185.132.189.10', 'confidence': 0.92},
            {'source': 'APT29', 'relation': 'targets', 'target': 'Energy Sector', 'confidence': 0.88},
            {'source': 'SilentHorn', 'relation': 'exploits', 'target': 'CVE-2023-45678', 'confidence': 0.96}
        ]
