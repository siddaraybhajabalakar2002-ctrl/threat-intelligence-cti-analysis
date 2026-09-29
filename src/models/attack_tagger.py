import re
from typing import Dict, Any

class AttackTagger:
    def __init__(self):
        # Comprehensive keyword-to-technique mapping with word-boundary safety
        self.technique_map = {
            'phishing': ('T1566', 'Phishing'),
            'spear-phishing': ('T1566', 'Phishing'),
            'spearphishing': ('T1566', 'Phishing'),
            'attachment': ('T1566', 'Phishing'),
            'exploit': ('T1190', 'Exploit Public-Facing Application'),
            'vulnerability': ('T1190', 'Exploit Public-Facing Application'),
            'zero-day': ('T1190', 'Exploit Public-Facing Application'),
            'cve': ('T1190', 'Exploit Public-Facing Application'),
            'user execution': ('T1204', 'User Execution'),
            'click': ('T1204', 'User Execution'),
            'powershell': ('T1059.001', 'PowerShell'),
            'cmd': ('T1059.003', 'Windows Command Shell'),
            'command shell': ('T1059.003', 'Windows Command Shell'),
            'bash': ('T1059.004', 'Unix Shell'),
            'script': ('T1059', 'Command and Scripting Interpreter'),
            'command': ('T1059', 'Command and Scripting Interpreter'),
            'registry': ('T1547', 'Registry Run Keys / Startup Folder'),
            'run key': ('T1547', 'Registry Run Keys / Startup Folder'),
            'hkey': ('T1547', 'Registry Run Keys / Startup Folder'),
            'scheduled task': ('T1053', 'Scheduled Task/Job'),
            'cron': ('T1053.003', 'Cron'),
            'process hollowing': ('T1055.012', 'Process Hollowing'),
            'process injection': ('T1055', 'Process Injection'),
            'injection': ('T1055', 'Process Injection'),
            'masquerading': ('T1036', 'Masquerading'),
            'evasion': ('T1036', 'Masquerading'),
            'tunneling': ('T1071', 'Application Layer Protocol'),
            'dns tunneling': ('T1071.004', 'DNS Protocol'),
            'c2': ('T1071', 'Application Layer Protocol'),
            'command and control': ('T1071', 'Application Layer Protocol'),
            'beacon': ('T1071', 'Application Layer Protocol'),
            'beaconing': ('T1071', 'Application Layer Protocol'),
            'exfiltration': ('T1041', 'Exfiltration Over C2 Channel'),
            'exfiltrate': ('T1041', 'Exfiltration Over C2 Channel'),
            'obfuscation': ('T1027', 'Obfuscated Files or Information'),
            'encrypted': ('T1027', 'Obfuscated Files or Information'),
            'encryption': ('T1027', 'Obfuscated Files or Information'),
            'aes': ('T1027', 'Obfuscated Files or Information'),
            'credential dumping': ('T1003', 'OS Credential Dumping'),
            'mimikatz': ('T1003', 'OS Credential Dumping'),
            'brute force': ('T1110', 'Brute Force'),
            'password spray': ('T1110.003', 'Password Spraying'),
            'lateral movement': ('T1021', 'Remote Services'),
            'rdp': ('T1021.001', 'Remote Desktop Protocol'),
            'smb': ('T1021.002', 'SMB/Windows Admin Shares'),
            'ransomware': ('T1486', 'Data Encrypted for Impact'),
            'wipe': ('T1485', 'Data Destruction'),
            'valid accounts': ('T1078', 'Valid Accounts')
        }

        # Technique ID to authoritative name mapping (allows direct lookup by ID)
        self.known_technique_names = {
            'T1566': 'Phishing',
            'T1190': 'Exploit Public-Facing Application',
            'T1204': 'User Execution',
            'T1059': 'Command and Scripting Interpreter',
            'T1059.001': 'PowerShell',
            'T1059.003': 'Windows Command Shell',
            'T1059.004': 'Unix Shell',
            'T1547': 'Registry Run Keys / Startup Folder',
            'T1053': 'Scheduled Task/Job',
            'T1053.003': 'Cron',
            'T1055': 'Process Injection',
            'T1055.012': 'Process Hollowing',
            'T1036': 'Masquerading',
            'T1071': 'Application Layer Protocol',
            'T1071.004': 'DNS Protocol',
            'T1041': 'Exfiltration Over C2 Channel',
            'T1027': 'Obfuscated Files or Information',
            'T1003': 'OS Credential Dumping',
            'T1110': 'Brute Force',
            'T1021': 'Remote Services',
            'T1486': 'Data Encrypted for Impact',
            'T1485': 'Data Destruction',
            'T1078': 'Valid Accounts',
            'T1595': 'Active Scanning',
            'T1057': 'Process Discovery'
        }

        # MITRE ATT&CK Tactic Mapping
        self.tactic_map = {
            'T1566': ('TA0001', 'Initial Access'),
            'T1190': ('TA0001', 'Initial Access'),
            'T1078': ('TA0001', 'Initial Access'),
            'T1204': ('TA0002', 'Execution'),
            'T1059': ('TA0002', 'Execution'),
            'T1059.001': ('TA0002', 'Execution'),
            'T1059.003': ('TA0002', 'Execution'),
            'T1059.004': ('TA0002', 'Execution'),
            'T1547': ('TA0003', 'Persistence'),
            'T1053': ('TA0003', 'Persistence'),
            'T1053.003': ('TA0003', 'Persistence'),
            'T1055': ('TA0005', 'Defense Evasion'),
            'T1055.012': ('TA0005', 'Defense Evasion'),
            'T1036': ('TA0005', 'Defense Evasion'),
            'T1027': ('TA0005', 'Defense Evasion'),
            'T1003': ('TA0006', 'Credential Access'),
            'T1110': ('TA0006', 'Credential Access'),
            'T1057': ('TA0007', 'Discovery'),
            'T1595': ('TA0043', 'Reconnaissance'),
            'T1021': ('TA0008', 'Lateral Movement'),
            'T1071': ('TA0011', 'Command and Control'),
            'T1071.004': ('TA0011', 'Command and Control'),
            'T1041': ('TA0010', 'Exfiltration'),
            'T1486': ('TA0040', 'Impact'),
            'T1485': ('TA0040', 'Impact')
        }

        # Tactic IDs directly mentioned in text
        self.tactic_id_names = {
            'TA0043': 'Reconnaissance',
            'TA0042': 'Resource Development',
            'TA0001': 'Initial Access',
            'TA0002': 'Execution',
            'TA0003': 'Persistence',
            'TA0004': 'Privilege Escalation',
            'TA0005': 'Defense Evasion',
            'TA0006': 'Credential Access',
            'TA0007': 'Discovery',
            'TA0008': 'Lateral Movement',
            'TA0009': 'Collection',
            'TA0011': 'Command and Control',
            'TA0010': 'Exfiltration',
            'TA0040': 'Impact'
        }

        # Regex for direct MITRE technique IDs like T1566 or T1059.001
        self.technique_id_pattern = re.compile(r'\b(T\d{4}(?:\.\d{3})?)\b')
        self.tactic_id_pattern = re.compile(r'\b(TA\d{4})\b')

        # Precompile word-boundary regexes for each keyword to prevent substring false-positives
        self.compiled_keywords = {
            kw: re.compile(rf'\b{re.escape(kw)}\b', re.IGNORECASE)
            for kw in self.technique_map
        }

    def tag_report(self, text: str) -> Dict[str, Dict[str, str]]:
        if not text:
            return {'techniques': {}, 'tactics': {}}

        found_techniques = {}
        found_tactics = {}

        # 1. Direct MITRE Technique ID extraction from text (e.g. T1566, T1059)
        direct_tech_ids = self.technique_id_pattern.findall(text)
        for tid in direct_tech_ids:
            tech_name = self.known_technique_names.get(tid, f"ATT&CK Technique {tid}")
            found_techniques[tid] = tech_name
            # Resolve parent technique for sub-techniques if needed
            base_tid = tid.split('.')[0]
            if tid in self.tactic_map:
                tac_id, tac_name = self.tactic_map[tid]
                found_tactics[tac_id] = tac_name
            elif base_tid in self.tactic_map:
                tac_id, tac_name = self.tactic_map[base_tid]
                found_tactics[tac_id] = tac_name

        # 2. Direct MITRE Tactic ID extraction (e.g. TA0001, TA0002)
        direct_tac_ids = self.tactic_id_pattern.findall(text)
        for tac_id in direct_tac_ids:
            tac_name = self.tactic_id_names.get(tac_id, f"ATT&CK Tactic {tac_id}")
            found_tactics[tac_id] = tac_name

        # 3. Word-boundary keyword matching (prevents "recommendation" -> "cmd", "database" -> "aes")
        for keyword, pattern in self.compiled_keywords.items():
            if pattern.search(text):
                tech_id, tech_name = self.technique_map[keyword]
                found_techniques[tech_id] = tech_name

                # Add corresponding tactic
                base_tid = tech_id.split('.')[0]
                if tech_id in self.tactic_map:
                    tactic_id, tactic_name = self.tactic_map[tech_id]
                    found_tactics[tactic_id] = tactic_name
                elif base_tid in self.tactic_map:
                    tactic_id, tactic_name = self.tactic_map[base_tid]
                    found_tactics[tactic_id] = tactic_name

        return {
            'techniques': found_techniques,
            'tactics': found_tactics
        }
