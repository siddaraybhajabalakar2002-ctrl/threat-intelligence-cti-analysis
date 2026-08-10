class AttackTagger:
    def __init__(self):
        # A simple keyword mapping for the demonstration
        self.technique_map = {
            'phishing': ('T1566', 'Phishing'),
            'spear-phishing': ('T1566', 'Phishing'),
            'attachment': ('T1566', 'Phishing'),
            'exploit': ('T1190', 'Exploit Public-Facing Application'),
            'vulnerability': ('T1190', 'Exploit Public-Facing Application'),
            'zero-day': ('T1190', 'Exploit Public-Facing Application'),
            'cve': ('T1190', 'Exploit Public-Facing Application'),
            'execution': ('T1204', 'User Execution'),
            'click': ('T1204', 'User Execution'),
            'command': ('T1059', 'Command and Scripting Interpreter'),
            'script': ('T1059', 'Command and Scripting Interpreter'),
            'powershell': ('T1059', 'Command and Scripting Interpreter'),
            'cmd': ('T1059', 'Command and Scripting Interpreter'),
            'registry': ('T1547', 'Registry Run Keys / Startup Folder'),
            'hkey': ('T1547', 'Registry Run Keys / Startup Folder'),
            'scheduled task': ('T1053', 'Scheduled Task/Job'),
            'process hollowing': ('T1055', 'Process Injection'),
            'injection': ('T1055', 'Process Injection'),
            'evasion': ('T1036', 'Masquerading'),
            'tunneling': ('T1071', 'Application Layer Protocol'),
            'c2': ('T1041', 'Exfiltration Over C2 Channel'),
            'exfiltration': ('T1041', 'Exfiltration Over C2 Channel'),
            'encryption': ('T1027', 'Obfuscated Files or Information'),
            'aes': ('T1027', 'Obfuscated Files or Information')
        }

        self.tactic_map = {
            'T1566': ('TA0001', 'Initial Access'),
            'T1190': ('TA0001', 'Initial Access'),
            'T1204': ('TA0002', 'Execution'),
            'T1059': ('TA0002', 'Execution'),
            'T1547': ('TA0003', 'Persistence'),
            'T1053': ('TA0003', 'Persistence'),
            'T1055': ('TA0005', 'Defense Evasion'),
            'T1036': ('TA0005', 'Defense Evasion'),
            'T1027': ('TA0005', 'Defense Evasion'),
            'T1071': ('TA0011', 'Command and Control'),
            'T1041': ('TA0010', 'Exfiltration')
        }

    def tag_report(self, text):
        text_lower = text.lower()
        found_techniques = {}
        found_tactics = {}

        # Scan for techniques
        for keyword, (tech_id, tech_name) in self.technique_map.items():
            if keyword in text_lower:
                found_techniques[tech_id] = tech_name

                # Add the corresponding tactic if it maps directly
                if tech_id in self.tactic_map:
                    tactic_id, tactic_name = self.tactic_map[tech_id]
                    found_tactics[tactic_id] = tactic_name

        return {
            'techniques': found_techniques,
            'tactics': found_tactics
        }
