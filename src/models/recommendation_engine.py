class RecommendationEngine:
    def __init__(self):
        # MITRE ATT&CK Mitigations mapping
        self.mitigation_map = {
            'T1566': {
                "type": "ATTACK VECTOR: PHISHING",
                "understanding": "Phishing (T1566) was identified as an initial access vector.",
                "explanation": "Implement email filtering, enforce Multi-Factor Authentication (MFA), and conduct anti-phishing user training.",
                "how_to_do_it": "1. Go to your email gateway settings and enable strict SPF/DKIM validation.\n2. Force MFA for all users via Azure AD or Okta.\n3. Run a simulated phishing campaign using platforms like KnowBe4.",
                "more_info": "Use SPF, DKIM, and DMARC to prevent email spoofing. Reference MITRE Mitigation M1054."
            },
            'T1190': {
                "type": "VULNERABILITY EXPLOIT",
                "understanding": "Exploitation of Public-Facing Applications (T1190) detected.",
                "explanation": "Conduct vulnerability scanning on public-facing assets and immediately apply security patches or WAF rules.",
                "how_to_do_it": "1. Run Nessus or OpenVAS against all external IP ranges.\n2. Log into your WAF (e.g., Cloudflare/AWS WAF) and enable managed rule sets for known CVEs.\n3. Apply vendor patches to affected servers during the next emergency change window.",
                "more_info": "Reference MITRE Mitigation M1016 (Vulnerability Scanning) and M1050 (Exploit Protection)."
            },
            'T1204': {
                "type": "USER EXECUTION",
                "understanding": "User Execution (T1204) relies on user interaction to execute malicious code.",
                "explanation": "Restrict execution of untrusted files using AppLocker or Windows Defender Application Control (WDAC).",
                "how_to_do_it": "1. Open Group Policy Management (GPMC).\n2. Navigate to Computer Configuration > Windows Settings > Security Settings > Application Control Policies.\n3. Create default AppLocker rules to allow execution only from C:\\Program Files and C:\\Windows.",
                "more_info": "Ensure EDR solutions are configured to detect malicious child processes spawning from common applications."
            },
            'T1059': {
                "type": "COMMAND & SCRIPTING",
                "understanding": "Command and Scripting Interpreter (T1059) such as PowerShell or CMD is being used for execution.",
                "explanation": "Enforce PowerShell execution policies, enable Script Block Logging (Event ID 4104), and restrict command line access.",
                "how_to_do_it": "1. In Group Policy, set 'Turn on PowerShell Script Block Logging' to Enabled.\n2. Set Execution Policy to 'RemoteSigned' or 'Restricted'.\n3. Use Endpoint Privilege Management to block CMD.exe for non-admin users.",
                "more_info": "Monitor command-line arguments for obfuscation or base64 encoding."
            },
            'T1547': {
                "type": "PERSISTENCE MECHANISM",
                "understanding": "Registry Run Keys / Startup Folder (T1547) identified for persistence.",
                "explanation": "Monitor registry modifications to HKCU/HKLM Run keys and startup folder additions.",
                "how_to_do_it": "1. Deploy Sysmon to all endpoints.\n2. Configure Sysmon Event ID 12, 13, and 14 to log all changes to \\Software\\Microsoft\\Windows\\CurrentVersion\\Run.\n3. Create an SIEM alert for unauthorized registry additions.",
                "more_info": "Use Sysmon Event ID 12/13/14 to detect unauthorized registry changes."
            },
            'T1055': {
                "type": "DEFENSE EVASION",
                "understanding": "Process Injection (T1055) is used to hide malicious code execution.",
                "explanation": "Ensure EDR is configured for memory scanning to detect injected threads and process hollowing.",
                "how_to_do_it": "1. Access your EDR console (e.g., CrowdStrike, SentinelOne).\n2. Ensure 'Aggressive Memory Scanning' or similar heuristic prevention is enabled.\n3. Review alerts for 'Unexpected Child Process' under legitimate binaries like svchost.exe.",
                "more_info": "Look for unexpected network connections originating from legitimate processes like svchost.exe."
            },
            'T1041': {
                "type": "DATA EXFILTRATION",
                "understanding": "Data Exfiltration Over C2 Channel (T1041) detected.",
                "explanation": "Implement Data Loss Prevention (DLP) and monitor for large, anomalous outbound data transfers.",
                "how_to_do_it": "1. Create firewall rules to block outbound traffic on non-standard ports.\n2. Configure your network IDS/IPS (e.g., Zeek, Suricata) to alert on connections transmitting >50MB to unknown external IPs.\n3. Enable DLP policies in your email and endpoint agents.",
                "more_info": "Restrict outbound traffic using strict firewall rules (default deny)."
            }
        }

    def generate_recommendations(self, entities, attack_tags, severity):
        recommendations = []
        
        # 1. Technique-specific mitigations
        techniques = attack_tags.get('techniques', {})
        for tech_id, tech_name in techniques.items():
            if tech_id in self.mitigation_map:
                recommendations.append(self.mitigation_map[tech_id])
                
        # 2. Entity-specific mitigations
        if entities.get('malware'):
            malware_names = ', '.join(entities['malware'][:3])
            recommendations.append({
                "type": "MALWARE RESPONSE",
                "understanding": f"Specific malware families ({malware_names}) were identified in the analysis.",
                "explanation": f"Isolate systems exhibiting signs of {malware_names} infection. Update EDR signatures and block associated IOCs.",
                "how_to_do_it": f"1. Use your EDR tool to Network Isolate the affected host immediately.\n2. Add the provided file hashes and domains to your EDR and Firewall blocklists.\n3. Run a full disk antivirus scan to remove {malware_names} artifacts.",
                "more_info": "Perform a complete organizational sweep for these specific malware indicators."
            })
            
        if entities.get('cve'):
            cves = ', '.join(entities['cve'][:3])
            recommendations.append({
                "type": "CVE PATCHING",
                "understanding": f"Specific Common Vulnerabilities and Exposures ({cves}) were referenced.",
                "explanation": f"Prioritize testing and deployment of patches for {cves}.",
                "how_to_do_it": f"1. Identify all internal systems vulnerable to {cves} using your vulnerability scanner.\n2. Download the official patch from the vendor.\n3. Deploy the patch via your patch management system (e.g., SCCM, Intune) after testing.",
                "more_info": "Check CISA's Known Exploited Vulnerabilities (KEV) catalog for these CVEs and adhere to strict patching timelines."
            })
            
        if entities.get('threat_actor'):
            actors = ', '.join(entities['threat_actor'][:3])
            recommendations.append({
                "type": "ACTOR TRACKING",
                "understanding": f"Activity attributed to known threat groups ({actors}).",
                "explanation": f"Review dedicated threat intelligence reports for {actors} to understand their complete attack lifecycle.",
                "how_to_do_it": f"1. Search your Threat Intel Platform (TIP) for {actors}.\n2. Extract all known TTPs (Tactics, Techniques, and Procedures).\n3. Proactively hunt in your SIEM for logs matching these TTPs.",
                "more_info": "Pivot on known IOCs associated with these actors in your SIEM/XDR to find historical compromises."
            })

        # 3. Fallback / Baseline
        if not recommendations:
            if severity.get('score', 0) >= 7.0:
                recommendations.append({
                    "type": "CRITICAL INCIDENT",
                    "understanding": "High severity threat detected but no specific techniques were mapped.",
                    "explanation": "Initiate generic incident response procedures and isolate affected assets.",
                    "how_to_do_it": "1. Convene the Incident Response team.\n2. Identify potentially compromised assets via SIEM alerts.\n3. Isolate assets and capture memory/disk images for forensics.",
                    "more_info": "Conduct deeper forensics and manual log review to identify the attack vector."
                })
            else:
                recommendations.append({
                    "type": "BASELINE MONITORING",
                    "understanding": "No specific actionable techniques or critical entities were extracted.",
                    "explanation": "Continue standard security monitoring, endpoint protection, and regular patching.",
                    "how_to_do_it": "1. Review daily SIEM dashboards for anomalies.\n2. Ensure AV/EDR agents are online and updated.\n3. Schedule the next routine vulnerability scan.",
                    "more_info": "Ensure all standard telemetry (Sysmon, EDR, Firewall) is functioning normally."
                })
                
        # Deduplicate recommendations by type
        unique_recs = []
        seen_types = set()
        for rec in recommendations:
            if rec['type'] not in seen_types:
                unique_recs.append(rec)
                seen_types.add(rec['type'])
                
        # Limit to top 5
        return unique_recs[:5]
