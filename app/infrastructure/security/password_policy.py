import re
from typing import Tuple

class PasswordPolicy:
    """ISO 27001 A.9.4.3 Password management system"""
    
    MIN_LENGTH = 8
    PASSWORD_RULES = [
        (r"[A-Z]", "uppercase letter"),
        (r"[a-z]", "lowercase letter"),
        (r"\d", "number"),
        (r"[!@#$%^&*]", "special character")
    ]
    
    @classmethod
    def validate_password(cls, password: str) -> Tuple[bool, str]:
        # Check minimum length
        if len(password) < cls.MIN_LENGTH:
            return False, f"Password must be at least {cls.MIN_LENGTH} characters"
        
        # Check each rule
        for pattern, requirement in cls.PASSWORD_RULES:
            if not re.search(pattern, password):
                return False, f"Password must contain at least one {requirement}"
        
        return True, "Password meets all requirements"