"""
Input Sanitizer Module
Protects against malicious inputs and prompt injection attacks
"""

import re
import html
from typing import List, Dict, Tuple
from datetime import datetime
from loguru import logger
import hashlib

class InputSanitizer:
    """Sanitize user inputs to prevent security issues"""
    
    def __init__(self):
        # Dangerous patterns that could indicate injection attempts
        self.dangerous_patterns = [
            # Prompt injection attempts
            "ignore previous instructions",
            "ignore all previous",
            "disregard previous",
            "forget previous instructions",
            "new instructions:",
            "you are now",
            "you must now",
            "from now on",
            "system:",
            "assistant:",
            "user:",
            
            # Role manipulation
            "act as",
            "pretend to be",
            "roleplay as",
            "you are a",
            "behave like",
            
            # Command injection
            "execute:",
            "run command",
            "os.system",
            "subprocess",
            "eval(",
            "exec(",
            "__import__",
            
            # Data extraction attempts
            "show me your prompt",
            "what are your instructions",
            "reveal your",
            "display your system",
            "show configuration",
            "list your rules",
            
            # HTML/Script injection
            "<script",
            "javascript:",
            "onerror=",
            "onload=",
            "<iframe",
            "<object",
            "<embed",
            
            # SQL injection patterns
            "' or '1'='1",
            "drop table",
            "union select",
            "--",
            "/*",
            "*/",
            
            # Path traversal
            "../",
            "..\\",
            "/etc/passwd",
            "c:\\windows",
        ]
        
        # Compile regex patterns for efficiency
        self.injection_patterns = [
            re.compile(r'(ignore|disregard|forget)\s+(all\s+)?previous', re.IGNORECASE),
            re.compile(r'(system|assistant|user)\s*:', re.IGNORECASE),
            re.compile(r'<[^>]+>', re.IGNORECASE),  # HTML tags
            re.compile(r'[\'";].*;?\s*--', re.IGNORECASE),  # SQL injection
            re.compile(r'\.\.+[/\\]', re.IGNORECASE),  # Path traversal
        ]
        
        # PII detection patterns
        self.pii_patterns = [
            (r'\b\d{3}-\d{2}-\d{4}\b', 'SSN'),  # SSN
            (r'\b\d{16}\b', 'Credit Card'),     # Credit card
            (r'\b\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\b', 'Credit Card'),  # Spaced CC
            (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 'Email'),  # Email
            (r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', 'Phone'),  # Phone number
            (r'\b\d{5}(?:-\d{4})?\b', 'Zip Code'),  # Zip code
        ]
        
        # Sanitization log
        self.sanitization_log = []
        
    def sanitize_user_input(self, user_input: str, max_length: int = 500) -> str:
        """Main sanitization function for user inputs"""
        if not user_input:
            return ""
        
        original_input = user_input
        issues_found = []
        
        # Length check
        if len(user_input) > max_length:
            user_input = user_input[:max_length]
            issues_found.append("Truncated to max length")
        
        # HTML escape
        user_input = html.escape(user_input)
        
        # Check for dangerous patterns
        lower_input = user_input.lower()
        for pattern in self.dangerous_patterns:
            if pattern in lower_input:
                user_input = user_input.replace(pattern, "[FILTERED]")
                issues_found.append(f"Dangerous pattern: {pattern}")
        
        # Check regex patterns
        for pattern in self.injection_patterns:
            if pattern.search(user_input):
                user_input = pattern.sub("[FILTERED]", user_input)
                issues_found.append(f"Injection pattern detected")
        
        # Remove PII
        user_input, pii_found = self.remove_pii(user_input)
        if pii_found:
            issues_found.extend(pii_found)
        
        # Control character removal
        user_input = self.remove_control_characters(user_input)
        
        # Unicode normalization
        user_input = self.normalize_unicode(user_input)
        
        # Log if issues found
        if issues_found:
            self._log_sanitization(original_input, user_input, issues_found)
        
        return user_input.strip()
    
    def remove_pii(self, text: str) -> Tuple[str, List[str]]:
        """Remove personally identifiable information"""
        pii_found = []
        
        for pattern_str, pii_type in self.pii_patterns:
            pattern = re.compile(pattern_str)
            matches = pattern.findall(text)
            if matches:
                pii_found.append(f"Found {pii_type}")
                text = pattern.sub(f"[{pii_type} REMOVED]", text)
        
        return text, pii_found
    
    def remove_control_characters(self, text: str) -> str:
        """Remove control characters except standard whitespace"""
        # Keep only printable characters and standard whitespace
        return ''.join(
            char for char in text 
            if char.isprintable() or char in '\n\r\t'
        )
    
    def normalize_unicode(self, text: str) -> str:
        """Normalize Unicode to prevent homograph attacks"""
        import unicodedata
        return unicodedata.normalize('NFKC', text)
    
    def validate_api_input(self, data: Dict) -> Tuple[bool, List[str]]:
        """Validate API input data structure"""
        issues = []
        
        # Check required fields
        if 'query' not in data:
            issues.append("Missing required field: query")
        
        # Validate field types
        if 'query' in data and not isinstance(data['query'], str):
            issues.append("Invalid type for query field")
        
        # Check for unexpected fields
        allowed_fields = {'query', 'user_id', 'context', 'test_mode'}
        unexpected = set(data.keys()) - allowed_fields
        if unexpected:
            issues.append(f"Unexpected fields: {unexpected}")
        
        # Sanitize each field
        if 'query' in data:
            data['query'] = self.sanitize_user_input(data['query'])
        
        if 'user_id' in data and data['user_id']:
            # Hash user ID for privacy
            data['user_id'] = self.hash_user_id(data['user_id'])
        
        return len(issues) == 0, issues
    
    def hash_user_id(self, user_id: str) -> str:
        """Hash user ID for privacy while maintaining uniqueness"""
        return hashlib.sha256(user_id.encode()).hexdigest()[:16]
    
    def detect_anomalous_input(self, text: str) -> Dict[str, any]:
        """Detect potentially anomalous input patterns"""
        anomalies = []
        
        # Check for excessive repetition
        words = text.split()
        if len(words) > 10:
            word_counts = {}
            for word in words:
                word_counts[word] = word_counts.get(word, 0) + 1
            
            max_repetition = max(word_counts.values())
            if max_repetition > len(words) * 0.3:  # More than 30% repetition
                anomalies.append("Excessive word repetition")
        
        # Check for suspicious character patterns
        if len(re.findall(r'[^\w\s]', text)) > len(text) * 0.3:  # More than 30% special chars
            anomalies.append("Excessive special characters")
        
        # Check for encoding attempts
        if any(pattern in text.lower() for pattern in ['base64', 'decode', 'encode', 'hex']):
            anomalies.append("Potential encoding attempt")
        
        # Check for suspicious URLs
        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, text)
        if urls:
            for url in urls:
                if any(suspicious in url.lower() for suspicious in ['bit.ly', 'tinyurl', 'goo.gl']):
                    anomalies.append("Suspicious shortened URL")
        
        return {
            "is_anomalous": len(anomalies) > 0,
            "anomalies": anomalies,
            "risk_level": self._calculate_risk_level(anomalies)
        }
    
    def _calculate_risk_level(self, anomalies: List[str]) -> str:
        """Calculate risk level based on anomalies"""
        if not anomalies:
            return "low"
        elif len(anomalies) == 1:
            return "medium"
        else:
            return "high"
    
    def _log_sanitization(self, original: str, sanitized: str, issues: List[str]):
        """Log sanitization events for security monitoring"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "original_preview": original[:100] + "..." if len(original) > 100 else original,
            "sanitized_preview": sanitized[:100] + "..." if len(sanitized) > 100 else sanitized,
            "issues": issues,
            "severity": "high" if any("injection" in issue.lower() for issue in issues) else "medium"
        }
        
        self.sanitization_log.append(log_entry)
        
        # Keep log size manageable
        if len(self.sanitization_log) > 1000:
            self.sanitization_log = self.sanitization_log[-500:]
        
        logger.warning(f"Input sanitization triggered: {issues}")
    
    def get_security_report(self) -> Dict:
        """Generate security report from sanitization logs"""
        if not self.sanitization_log:
            return {
                "total_incidents": 0,
                "status": "secure",
                "message": "No security incidents detected"
            }
        
        # Analyze incidents
        high_severity = sum(1 for log in self.sanitization_log if log["severity"] == "high")
        issue_types = {}
        
        for log in self.sanitization_log:
            for issue in log["issues"]:
                issue_type = issue.split(":")[0]
                issue_types[issue_type] = issue_types.get(issue_type, 0) + 1
        
        return {
            "total_incidents": len(self.sanitization_log),
            "high_severity_incidents": high_severity,
            "issue_types": issue_types,
            "recent_incidents": self.sanitization_log[-10:],
            "status": "alert" if high_severity > 5 else "monitored"
        }