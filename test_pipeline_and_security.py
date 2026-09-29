"""
Comprehensive Unit & Integration Test Suite for CTI Pipeline & Security Controls
Tests:
- NER Extractor (Refanging, IP validation, domain filtering, scheduled tasks, CVEs)
- ATT&CK Tagger (Word boundary isolation, direct ID extraction, tactic mapping)
- Relation Extractor (Dynamic context and semantic link extraction)
- Threat Scorer (Accurate severity calculation without empty list inflation)
- Knowledge Graph (Node, edge addition, D3 export groups)
- API Security (OTP brute force protection, timing attack defense, security headers)
"""
import os
import sys
import json
import time
import unittest

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(PROJECT_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from models.ner_extractor import CTINERExtractor, refang_text
from models.attack_tagger import AttackTagger
from models.relation_extractor import CTIRelationExtractor
from models.scorer import ThreatScorer
from kg.knowledge_graph import CTIKnowledgeGraph
from api.app import app, otp_store, users_db, MAX_OTP_ATTEMPTS


class TestCTINERExtractor(unittest.TestCase):
    def setUp(self):
        self.ner = CTINERExtractor()

    def test_refang_text(self):
        raw = "hxxps://evil[.]com/payload and 192[.]168[.]1[.]1 and admin[@]evil(.)org"
        refanged = refang_text(raw)
        self.assertIn("https://evil.com/payload", refanged)
        self.assertIn("192.168.1.1", refanged)
        self.assertIn("admin@evil.org", refanged)

    def test_ip_validation_and_rejection(self):
        text = "Valid: 185.132.189.10 and 10.0.0.1. Invalid: 999.999.999.999 and 1.2.3.999 and text.1.2.3"
        entities = self.ner.extract_all_entities(text)
        ips = entities.get('ip_address', [])
        self.assertIn("185.132.189.10", ips)
        self.assertIn("10.0.0.1", ips)
        self.assertNotIn("999.999.999.999", ips)
        self.assertNotIn("1.2.3.999", ips)

    def test_defanged_domains_and_file_extension_filtering(self):
        text = "Contact silentc2[.]net and malware.org. Do NOT extract report.pdf, payload.exe, or update.zip as domains."
        entities = self.ner.extract_all_entities(text)
        domains = entities.get('domain', [])
        self.assertIn("silentc2.net", domains)
        self.assertIn("malware.org", domains)
        self.assertNotIn("report.pdf", domains)
        self.assertNotIn("payload.exe", domains)
        self.assertNotIn("update.zip", domains)

    def test_url_extraction(self):
        text = "Phishing landing page at hxxp://evil-login.com/auth and https://c2.attacker.net/beacon"
        entities = self.ner.extract_all_entities(text)
        urls = entities.get('url', [])
        self.assertTrue(any("evil-login.com/auth" in u for u in urls))
        self.assertTrue(any("c2.attacker.net/beacon" in u for u in urls))

    def test_scheduled_task_extraction_no_garbage(self):
        text = 'creates a hidden scheduled task named "WindowsUpdateTask". 5. Monitor for scheduled task creation.'
        entities = self.ner.extract_all_entities(text)
        tasks = entities.get('scheduled_task', [])
        self.assertIn("WindowsUpdateTask", tasks)
        self.assertNotIn("named", tasks)
        self.assertNotIn("5", tasks)

    def test_cve_and_hashes(self):
        text = "Vulnerability CVE-2023-45678 exploited. Hashes: 5f3a8c9b2d4e6f1a0c5e8d3b7f9a1c4e6d8f2a5b9c3e7d1a4f6b8c2e0a5d9f3c and 098f6bcd4621d373cade4e832627b4f6"
        entities = self.ner.extract_all_entities(text)
        self.assertIn("CVE-2023-45678", entities.get('cve', []))
        self.assertIn("5f3a8c9b2d4e6f1a0c5e8d3b7f9a1c4e6d8f2a5b9c3e7d1a4f6b8c2e0a5d9f3c", entities.get('hash_sha256', []))
        self.assertIn("098f6bcd4621d373cade4e832627b4f6", entities.get('hash_md5', []))


class TestAttackTagger(unittest.TestCase):
    def setUp(self):
        self.tagger = AttackTagger()

    def test_word_boundary_isolation_prevents_false_positives(self):
        # "recommendation" must NOT trigger "cmd"
        # "database" must NOT trigger "aes"
        text = "We provide security recommendations for all enterprise databases."
        tags = self.tagger.tag_report(text)
        techniques = tags.get('techniques', {})
        self.assertNotIn('T1059.003', techniques, "False positive 'cmd' triggered on 'recommendation'")
        self.assertNotIn('T1027', techniques, "False positive 'aes' triggered on 'databases'")

    def test_legitimate_keyword_matches(self):
        text = "The malware spawned cmd.exe and executed a powershell script with AES encryption."
        tags = self.tagger.tag_report(text)
        techniques = tags.get('techniques', {})
        self.assertIn('T1059.003', techniques) # cmd
        self.assertIn('T1059.001', techniques) # powershell
        self.assertIn('T1027', techniques)     # aes

    def test_direct_technique_id_matching(self):
        text = "Adversary utilized technique T1566 and T1190 for initial access."
        tags = self.tagger.tag_report(text)
        techniques = tags.get('techniques', {})
        tactics = tags.get('tactics', {})
        self.assertIn('T1566', techniques)
        self.assertIn('T1190', techniques)
        self.assertIn('TA0001', tactics) # Initial Access


class TestRelationExtractor(unittest.TestCase):
    def setUp(self):
        self.extractor = CTIRelationExtractor()

    def test_dynamic_relation_extraction(self):
        text = "Lazarus Group deployed BlackBasta to attack Healthcare. BlackBasta communicates with 198.51.100.22."
        relations = self.extractor.extract_all_relations(text)
        self.assertTrue(len(relations) >= 2)
        
        rel_types = {(r['source'], r['relation'], r['target']) for r in relations}
        self.assertIn(('Lazarus Group', 'uses', 'BlackBasta'), rel_types)
        self.assertIn(('BlackBasta', 'communicates_with', '198.51.100.22'), rel_types)


class TestThreatScorer(unittest.TestCase):
    def setUp(self):
        self.scorer = ThreatScorer()

    def test_empty_lists_do_not_inflate_score(self):
        # Empty entities should not get base weight
        empty_entities = {'threat_actor': [], 'malware': [], 'cve': []}
        empty_attack_tags = {'techniques': {}, 'tactics': {}}
        res = self.scorer.calculate_severity(empty_entities, empty_attack_tags)
        self.assertEqual(res['score'], 0.0)
        self.assertEqual(res['level'], "LOW")

    def test_high_severity_calculation(self):
        entities = {
            'threat_actor': ['APT29'],
            'malware': ['SilentHorn'],
            'cve': ['CVE-2023-45678'],
            'ip_address': ['185.132.189.10']
        }
        attack_tags = {
            'tactics': {'TA0010': 'Exfiltration', 'TA0040': 'Impact'}
        }
        res = self.scorer.calculate_severity(entities, attack_tags)
        self.assertTrue(res['score'] >= 7.0)
        self.assertIn(res['level'], ["HIGH", "CRITICAL"])


class TestKnowledgeGraph(unittest.TestCase):
    def setUp(self):
        self.kg = CTIKnowledgeGraph()

    def test_d3_export_groups(self):
        entities = {
            'threat_actor': ['APT29'],
            'malware': ['SilentHorn'],
            'ip_address': ['185.132.189.10'],
            'cve': ['CVE-2023-45678']
        }
        self.kg.add_entities_from_ner(entities)
        self.kg.add_relations_from_extraction([
            {'source': 'APT29', 'target': 'SilentHorn', 'relation': 'uses', 'confidence': 0.95}
        ])
        
        d3_data = self.kg.export_d3()
        nodes = {n['id']: n['group'] for n in d3_data['nodes']}
        self.assertEqual(nodes.get('APT29'), 'ThreatActor')
        self.assertEqual(nodes.get('SilentHorn'), 'Malware')
        self.assertEqual(nodes.get('185.132.189.10'), 'IPAddress')
        self.assertEqual(nodes.get('CVE-2023-45678'), 'CVE')
        self.assertEqual(len(d3_data['links']), 1)


class TestAPISecurityAndEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        otp_store.clear()
        users_db["testuser@example.com"] = {"username": "Test User", "email": "testuser@example.com"}

    def test_security_headers_present(self):
        res = self.client.get('/health')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.headers.get('X-Content-Type-Options'), 'nosniff')
        self.assertEqual(res.headers.get('X-Frame-Options'), 'SAMEORIGIN')
        self.assertEqual(res.headers.get('X-XSS-Protection'), '1; mode=block')

    def test_otp_brute_force_lockout(self):
        email = "testuser@example.com"
        otp_store[email] = {
            "otp": "777888",
            "expires_at": time.time() + 300,
            "attempts": 0,
            "last_requested": time.time(),
            "pending_user": None
        }

        # Submit 5 incorrect guesses
        for i in range(MAX_OTP_ATTEMPTS):
            res = self.client.post('/api/auth/verify-otp', json={
                "email": email,
                "otp": f"00000{i}"
            })
            self.assertEqual(res.status_code, 401)
            data = res.get_json()
            self.assertIn("attempt(s) remaining", data["error"])

        # 6th attempt should result in 429 Too Many Requests and invalidate the OTP
        res_locked = self.client.post('/api/auth/verify-otp', json={
            "email": email,
            "otp": "000006"
        })
        self.assertEqual(res_locked.status_code, 429)
        self.assertNotIn(email, otp_store, "OTP was not revoked after brute force attempts exceeded")

    def test_successful_otp_login(self):
        email = "testuser@example.com"
        otp_store[email] = {
            "otp": "123456",
            "expires_at": time.time() + 300,
            "attempts": 0,
            "last_requested": time.time(),
            "pending_user": None
        }

        res = self.client.post('/api/auth/verify-otp', json={
            "email": email,
            "otp": "123456"
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["user"]["email"], email)
        self.assertNotIn(email, otp_store, "OTP was not consumed after successful login")

    def test_get_existing_users(self):
        res = self.client.get('/api/auth/users')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIsInstance(data["users"], list)
        emails = [u["email"] for u in data["users"]]
        self.assertIn("testuser@example.com", emails)

    def test_logout_endpoint(self):
        res = self.client.post('/api/auth/logout', json={"email": "testuser@example.com"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])

    def test_login_page_endpoint(self):
        res = self.client.get('/login')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Analyst Authentication", res.data)
        self.assertIn(b"CTI ANALYSIS", res.data)

    def test_analyze_endpoint(self):
        report = "APT28 launched a phishing campaign targeting Healthcare with malware RedLine at c2.host[.]net"
        res = self.client.post('/analyze', json={"report_text": report})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("entities", data)
        self.assertIn("attack_tags", data)
        self.assertIn("relations", data)
        self.assertIn("severity", data)
        self.assertIn("recommendations", data)


if __name__ == '__main__':
    unittest.main()

