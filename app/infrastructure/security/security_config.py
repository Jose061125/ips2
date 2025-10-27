from typing import Dict, Any

class SecurityConfig:
    """ISO 27001 A.14.2.5 Secure Development Configuration"""
    SETTINGS: Dict[str, Any] = {
        'PASSWORD_MIN_LENGTH': 8,
        'MAX_LOGIN_ATTEMPTS': 3,
        'SESSION_TIMEOUT': 30,
        'ALLOWED_HOSTS': ['localhost', '127.0.0.1'],
        'CSRF_ENABLED': True,
        'LOG_LEVEL': 'INFO'
    }

    @classmethod
    def get(cls, key: str) -> Any:
        return cls.SETTINGS.get(key)