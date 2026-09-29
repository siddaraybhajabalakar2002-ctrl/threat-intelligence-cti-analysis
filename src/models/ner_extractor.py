import re
import ipaddress
import logging
from typing import Dict, List, Any

logger = logging.getLogger("CTINERExtractor")

# File extensions that should NEVER be classified as domains
COMMON_FILE_EXTENSIONS = {
    'exe', 'dll', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
    'zip', 'tar', 'gz', '7z', 'rar', 'bin', 'sys', 'sh', 'bat', 'ps1',
    'py', 'c', 'cpp', 'h', 'txt', 'csv', 'log', 'json', 'xml', 'html',
    'png', 'jpg', 'jpeg', 'gif', 'md', 'cfg', 'conf', 'ini', 'vbs', 'js'
}

# Known Threat Actors for resilient matching
KNOWN_THREAT_ACTORS = [
    "APT29", "APT28", "Cozy Bear", "Fancy Bear", "Lazarus Group", "Lazarus",
    "FIN7", "FIN8", "FIN11", "LockBit", "BlackCat", "Sandworm", "Dragonfly",
    "Wizard Spider", "Turla", "OilRig", "Carbanak", "Charming Kitten",
    "Kimsuky", "Silence", "DarkSide", "REvil", "Conti", "Scattered Spider"
]

# Known Malware Families for resilient matching
KNOWN_MALWARE = [
    "SilentHorn", "Emotet", "TrickBot", "Cobalt Strike", "Qakbot", "Agent Tesla",
    "RedLine", "RedLine Stealer", "IcedID", "FormBook", "WannaCry", "DarkSide",
    "REvil", "Conti", "BazarLoader", "Dridex", "Mimikatz", "AsyncRAT", "Mirai",
    "Ryuk", "BlackBasta", "LockBit", "Ursnif", "NjRAT", "Remcos"
]


def refang_text(text: str) -> str:
    """Normalize defanged indicators (e.g., evil[.]com -> evil.com, hxxp:// -> http://)."""
    if not text:
        return ""
    # Refang brackets around dots
    s = re.sub(r'\[\.\]|\(\.\)|\{\.\}|\\\.|\s*\.\s*', '.', text)
    # Refang brackets around colons
    s = re.sub(r'\[:\]|\(:\)', ':', s)
    # Refang brackets around @
    s = re.sub(r'\[@\]|\(@\)', '@', s)
    # Refang hxxp / hxxps
    s = re.sub(r'\bhxxp://', 'http://', s, flags=re.IGNORECASE)
    s = re.sub(r'\bhxxps://', 'https://', s, flags=re.IGNORECASE)
    return s


class CTINERExtractor:
    def __init__(self):
        # Load spaCy model for general NLP entities with safe fallback
        self.nlp = None
        try:
            import spacy
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except Exception:
                try:
                    # Attempt lightweight blank English pipeline
                    self.nlp = spacy.blank("en")
                    if "sentencizer" not in self.nlp.pipe_names:
                        self.nlp.add_pipe("sentencizer")
                except Exception as e:
                    logger.warning(f"Could not load spaCy model: {e}. Fallback to rule-based NER.")
                    self.nlp = None
        except ImportError:
            logger.warning("spaCy not installed; using pure regex/rule-based NER.")
            self.nlp = None

        # Compile regular expressions for hard IOCs (Indicators of Compromise)
        self.raw_ip_pattern = re.compile(r'\b(?:\d{1,3}(?:\[\.\]|\.)){3}\d{1,3}\b')
        self.url_pattern = re.compile(r'\b(?:https?|hxxps?):\/\/[^\s<>"\'{}|\\^`]+', re.IGNORECASE)
        self.domain_pattern = re.compile(r'\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b')
        self.defanged_domain_pattern = re.compile(r'\b(?:[a-zA-Z0-9-]+\[\.\])+[a-zA-Z]{2,}\b', re.IGNORECASE)
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+(?:@|\[@\])[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')
        self.hash_md5 = re.compile(r'\b[a-fA-F0-9]{32}\b')
        self.hash_sha1 = re.compile(r'\b[a-fA-F0-9]{40}\b')
        self.hash_sha256 = re.compile(r'\b[a-fA-F0-9]{64}\b')
        self.cve_pattern = re.compile(r'\bCVE-\d{4}-\d{4,7}\b', re.IGNORECASE)
        self.registry_pattern = re.compile(
            r'\b(?:HKEY_CURRENT_USER|HKCU|HKEY_LOCAL_MACHINE|HKLM|HKEY_CLASSES_ROOT|HKCR|HKEY_USERS|HKU|HKEY_CURRENT_CONFIG|HKCC)\\[a-zA-Z0-9_\\\-]+\b',
            re.IGNORECASE
        )

    def is_valid_ipv4(self, ip_str: str) -> bool:
        """Validate if a string is a legitimate IPv4 address with octets 0-255."""
        clean_ip = ip_str.replace('[.]', '.')
        try:
            ip = ipaddress.IPv4Address(clean_ip)
            return True
        except (ValueError, ipaddress.AddressValueError):
            return False

    def is_valid_domain(self, domain_str: str) -> bool:
        """Check if candidate domain has valid format and is not a common file or IP."""
        clean = domain_str.replace('[.]', '.').lower().strip('.')
        parts = clean.split('.')
        if len(parts) < 2:
            return False
        tld = parts[-1]
        # Ignore file extensions
        if tld in COMMON_FILE_EXTENSIONS:
            return False
        # Ignore if all parts are numeric (handled as IP)
        if all(part.isdigit() for part in parts):
            return False
        # TLD must be letters
        if not tld.isalpha() or len(tld) < 2:
            return False
        return True

    def extract_all_entities(self, text: str) -> Dict[str, List[str]]:
        if not text:
            return {}

        entities = {
            'threat_actor': [],
            'malware': [],
            'hash_sha256': [],
            'hash_md5': [],
            'hash_sha1': [],
            'ip_address': [],
            'domain': [],
            'url': [],
            'email': [],
            'registry_key': [],
            'scheduled_task': [],
            'cve': []
        }

        # 1. URLs (extract before domain parsing so domain doesn't double-count fragments)
        urls = self.url_pattern.findall(text)
        if urls:
            entities['url'] = list(dict.fromkeys(refang_text(u).rstrip('.,;:)') for u in urls))

        # 2. IP Addresses (Validating octets 0-255 and refanging)
        raw_ips = self.raw_ip_pattern.findall(text)
        valid_ips = []
        for raw_ip in raw_ips:
            clean_ip = raw_ip.replace('[.]', '.')
            if self.is_valid_ipv4(clean_ip):
                valid_ips.append(clean_ip)
        if valid_ips:
            entities['ip_address'] = list(dict.fromkeys(valid_ips))

        # 3. Domains (Standard and Defanged)
        found_domains = []
        # Check defanged domains first (e.g. silentc2[.]net)
        for d in self.defanged_domain_pattern.findall(text):
            refanged = d.replace('[.]', '.')
            if self.is_valid_domain(refanged):
                found_domains.append(refanged)
        # Check standard domains
        for d in self.domain_pattern.findall(text):
            if self.is_valid_domain(d):
                found_domains.append(d)
        if found_domains:
            # Deduplicate while preserving order
            entities['domain'] = list(dict.fromkeys(found_domains))

        # 4. Emails
        emails = self.email_pattern.findall(text)
        if emails:
            entities['email'] = list(dict.fromkeys(refang_text(e) for e in emails))

        # 5. Hashes & CVEs
        sha256 = self.hash_sha256.findall(text)
        if sha256:
            entities['hash_sha256'] = list(dict.fromkeys(sha256))

        sha1 = self.hash_sha1.findall(text)
        if sha1:
            # Exclude strings that are part of SHA256 matches
            sha1_filtered = [h for h in sha1 if not any(h in s256 for s256 in entities['hash_sha256'])]
            if sha1_filtered:
                entities['hash_sha1'] = list(dict.fromkeys(sha1_filtered))

        md5 = self.hash_md5.findall(text)
        if md5:
            # Exclude strings that are part of longer hashes
            md5_filtered = [
                h for h in md5
                if not any(h in s256 for s256 in entities['hash_sha256'])
                and not any(h in s1 for s1 in entities.get('hash_sha1', []))
            ]
            if md5_filtered:
                entities['hash_md5'] = list(dict.fromkeys(md5_filtered))

        cves = self.cve_pattern.findall(text)
        if cves:
            entities['cve'] = list(dict.fromkeys([c.upper() for c in cves]))

        # 6. Registry Keys
        reg_keys = self.registry_pattern.findall(text)
        if reg_keys:
            entities['registry_key'] = list(dict.fromkeys(reg_keys))

        # 7. Scheduled Tasks (Fixing regex loophole: ignore 'named', numbers, and clean quotes)
        # Look for explicit quoted tasks or patterns like: task named "WindowsUpdateTask", scheduled task 'xyz', etc.
        task_candidates = []
        # Pattern 1: explicitly quoted task names
        task_pattern_quoted = re.findall(
            r'(?:scheduled\s+task|task(?:\s+name)?)\s+(?:named\s+|called\s+)?["\']([a-zA-Z0-9_\-\.]{3,})["\']',
            text, re.IGNORECASE
        )
        task_candidates.extend(task_pattern_quoted)

        # Pattern 2: task name keyword followed by name
        task_pattern_unquoted = re.findall(
            r'(?:task\s+named|scheduled\s+task\s+named)\s+([a-zA-Z0-9_\-\.]{3,})',
            text, re.IGNORECASE
        )
        task_candidates.extend(task_pattern_unquoted)

        # Pattern 3: direct key-value line: "- Scheduled Task: WindowsUpdateTask"
        task_pattern_kv = re.findall(
            r'(?:Scheduled\s+Task|task\s+name)\s*:\s*([a-zA-Z0-9_\-\.]{3,})',
            text, re.IGNORECASE
        )
        task_candidates.extend(task_pattern_kv)

        stopwords = {'named', 'called', 'created', 'the', 'this', 'that', 'with', 'from', 'each', 'some'}
        clean_tasks = []
        for t in task_candidates:
            clean = t.strip('"\'.: ')
            if clean and clean.lower() not in stopwords and not clean.isdigit() and len(clean) >= 3:
                clean_tasks.append(clean)
        if clean_tasks:
            entities['scheduled_task'] = list(dict.fromkeys(clean_tasks))

        # 8. Threat Actors & Malware (NLP + Robust Dictionary Matching)
        potential_actors = []
        potential_malware = []

        # SpaCy NLP if available
        if self.nlp is not None:
            try:
                doc = self.nlp(text[:100000])  # Cap length for safety
                for ent in getattr(doc, 'ents', []):
                    if ent.label_ in ['ORG', 'PERSON', 'PRODUCT']:
                        clean_ent = ent.text.strip()
                        if len(clean_ent) > 2 and clean_ent not in COMMON_FILE_EXTENSIONS:
                            potential_actors.append(clean_ent)
            except Exception as e:
                logger.debug(f"NLP entity pass error: {e}")

        # Heuristic for actors from NLP entities
        for actor in set(potential_actors):
            actor_upper = actor.upper()
            if any(keyword in actor_upper for keyword in ['APT', 'BEAR', 'GROUP', 'TEAM', 'HACKER', 'SPIDER', 'PANDA', 'KITTEN']):
                entities['threat_actor'].append(actor)

        # Check known threat actors directly via word boundary regex
        for known_actor in KNOWN_THREAT_ACTORS:
            pattern = rf'\b{re.escape(known_actor)}\b'
            if re.search(pattern, text, re.IGNORECASE):
                if not any(known_actor.lower() == existing.lower() for existing in entities['threat_actor']):
                    entities['threat_actor'].append(known_actor)

        # Check known malware families directly via word boundary regex
        for known_mal in KNOWN_MALWARE:
            pattern = rf'\b{re.escape(known_mal)}\b'
            if re.search(pattern, text, re.IGNORECASE):
                if not any(known_mal.lower() == existing.lower() for existing in entities['malware']):
                    entities['malware'].append(known_mal)

        # Return only the categories where we actually found something
        return {k: v for k, v in entities.items() if v}
