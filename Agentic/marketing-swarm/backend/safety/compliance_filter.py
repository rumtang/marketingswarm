"""
Compliance Filter Module
Ensures all content meets financial services regulatory requirements
"""

import re
from typing import Tuple, List, Dict, Set
from datetime import datetime
from loguru import logger

class ComplianceFilter:
    """Filter content to ensure SEC/FINRA compliance"""
    
    def __init__(self):
        # Forbidden phrases that violate regulations
        self.forbidden_phrases = [
            # Investment advice violations
            "guaranteed returns",
            "risk-free investment",
            "can't lose",
            "no risk",
            "guaranteed profit",
            "sure thing",
            "100% safe",
            
            # Specific recommendations
            "buy this stock",
            "sell this stock",
            "invest in",
            "you should buy",
            "you must invest",
            "perfect investment",
            
            # Misleading performance claims
            "always profitable",
            "never loses money",
            "beats the market every time",
            "outperforms all",
            
            # Unauthorized advice
            "personalized recommendation",
            "tailored to you",
            "based on your profile",
            "custom portfolio",
            
            # Promissory language
            "will make you rich",
            "will double your money",
            "expect returns of",
            "projected gains",
            
            # Insider information implications
            "inside information",
            "confidential tip",
            "not public yet",
            "exclusive information"
        ]
        
        # Required disclaimers
        self.required_disclaimers = [
            "This is for educational purposes only",
            "Not personalized financial advice",
            "Consult a licensed financial advisor",
            "Past performance does not guarantee future results"
        ]
        
        # Compliance log
        self.compliance_log = []
        
        # Pattern matchers for more complex violations
        self.violation_patterns = [
            re.compile(r'\b\d+%\s*(guaranteed|assured|certain)\b', re.IGNORECASE),
            re.compile(r'\b(buy|sell)\s+\w+\s+(stock|bond|fund)\b', re.IGNORECASE),
            re.compile(r'\bguarantee[ds]?\s+\d+%\b', re.IGNORECASE),
            re.compile(r'\b(hot|sure)\s+(tip|stock|pick)\b', re.IGNORECASE)
        ]
        
    def filter_query(self, query: str) -> Tuple[bool, str]:
        """Filter user queries for compliance issues"""
        original_query = query
        violations = []
        
        # Check for forbidden phrases
        lower_query = query.lower()
        for phrase in self.forbidden_phrases:
            if phrase in lower_query:
                violations.append(f"Forbidden phrase: {phrase}")
                query = query.replace(phrase, "[REMOVED]")
        
        # Check patterns
        for pattern in self.violation_patterns:
            matches = pattern.findall(query)
            if matches:
                violations.append(f"Pattern violation: {pattern.pattern}")
                query = pattern.sub("[REMOVED]", query)
        
        # Log if violations found
        if violations:
            self._log_compliance_issue("query", original_query, violations)
            return False, query
        
        return True, query
    
    def filter_response(self, response: str) -> str:
        """Filter agent responses for compliance"""
        original_response = response
        violations = []
        filtered_response = response
        
        # Check for forbidden phrases
        lower_response = response.lower()
        for phrase in self.forbidden_phrases:
            if phrase in lower_response:
                violations.append(f"Forbidden phrase: {phrase}")
                # Replace with compliant alternative
                filtered_response = self._replace_with_compliant(filtered_response, phrase)
        
        # Check patterns
        for pattern in self.violation_patterns:
            if pattern.search(filtered_response):
                violations.append(f"Pattern violation: {pattern.pattern}")
                filtered_response = pattern.sub("[COMPLIANCE: Removed specific advice]", filtered_response)
        
        # Add disclaimers if discussing investments
        if self._needs_disclaimer(filtered_response):
            filtered_response = self._add_disclaimer(filtered_response)
        
        # Log if violations found
        if violations:
            self._log_compliance_issue("response", original_response, violations)
        
        return filtered_response
    
    def validate_marketing_content(self, content: str) -> Dict[str, any]:
        """Comprehensive validation for marketing content"""
        issues = []
        warnings = []
        
        # Check forbidden content
        lower_content = content.lower()
        for phrase in self.forbidden_phrases:
            if phrase in lower_content:
                issues.append(f"Contains forbidden phrase: '{phrase}'")
        
        # Check for pattern violations
        for pattern in self.violation_patterns:
            if pattern.search(content):
                issues.append(f"Contains non-compliant pattern")
        
        # Check for required disclaimers
        has_disclaimer = any(
            disclaimer.lower() in lower_content 
            for disclaimer in self.required_disclaimers
        )
        
        if self._needs_disclaimer(content) and not has_disclaimer:
            warnings.append("Missing required disclaimer")
        
        # Check for testimonials without disclosure
        if "client said" in lower_content or "customer testimonial" in lower_content:
            if "results not typical" not in lower_content:
                warnings.append("Testimonial missing 'results not typical' disclosure")
        
        # Check for unsubstantiated claims
        if any(word in lower_content for word in ["best", "top", "leading", "#1"]):
            warnings.append("Contains superlative claims that may need substantiation")
        
        return {
            "compliant": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "requires_legal_review": len(issues) > 0 or len(warnings) > 2
        }
    
    def _replace_with_compliant(self, text: str, violation: str) -> str:
        """Replace violations with compliant alternatives"""
        replacements = {
            "guaranteed returns": "potential returns",
            "risk-free": "lower-risk",
            "can't lose": "designed to minimize risk",
            "no risk": "managed risk",
            "guaranteed profit": "profit potential",
            "sure thing": "opportunity",
            "100% safe": "relatively secure",
            "will make you rich": "has growth potential",
            "always profitable": "historically profitable",
            "beats the market": "competitive performance"
        }
        
        replacement = replacements.get(violation, "[removed for compliance]")
        return text.replace(violation, replacement)
    
    def _needs_disclaimer(self, text: str) -> bool:
        """Check if text discusses topics requiring disclaimers"""
        investment_keywords = [
            "invest", "return", "profit", "portfolio", "stock", "bond",
            "fund", "asset", "allocation", "strategy", "performance",
            "risk", "reward", "gain", "loss", "market", "trading"
        ]
        
        lower_text = text.lower()
        return any(keyword in lower_text for keyword in investment_keywords)
    
    def _add_disclaimer(self, text: str) -> str:
        """Add appropriate disclaimer to text"""
        disclaimer = "\n\n*Disclaimer: This content is for educational purposes only and does not constitute personalized financial advice. Please consult with a licensed financial advisor for recommendations specific to your situation.*"
        
        # Don't add if already has disclaimer
        if "disclaimer" in text.lower():
            return text
        
        return text + disclaimer
    
    def _log_compliance_issue(self, content_type: str, content: str, violations: List[str]):
        """Log compliance violations for audit trail"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": content_type,
            "content_preview": content[:200] + "..." if len(content) > 200 else content,
            "violations": violations,
            "action": "filtered"
        }
        
        self.compliance_log.append(log_entry)
        
        # Keep log size manageable
        if len(self.compliance_log) > 1000:
            self.compliance_log = self.compliance_log[-500:]
        
        logger.warning(f"Compliance violation in {content_type}: {violations}")
    
    def get_compliance_report(self) -> Dict:
        """Generate compliance report"""
        if not self.compliance_log:
            return {
                "total_violations": 0,
                "status": "clean",
                "message": "No compliance violations detected"
            }
        
        # Analyze violations
        violation_types = {}
        for entry in self.compliance_log:
            for violation in entry["violations"]:
                violation_type = violation.split(":")[0]
                violation_types[violation_type] = violation_types.get(violation_type, 0) + 1
        
        return {
            "total_violations": len(self.compliance_log),
            "violation_types": violation_types,
            "recent_violations": self.compliance_log[-10:],
            "status": "needs_review" if len(self.compliance_log) > 10 else "monitored"
        }
    
    def add_custom_rule(self, phrase: str, rule_type: str = "forbidden"):
        """Add custom compliance rule"""
        if rule_type == "forbidden":
            self.forbidden_phrases.append(phrase.lower())
            logger.info(f"Added forbidden phrase: {phrase}")
        elif rule_type == "pattern":
            pattern = re.compile(phrase, re.IGNORECASE)
            self.violation_patterns.append(pattern)
            logger.info(f"Added violation pattern: {phrase}")