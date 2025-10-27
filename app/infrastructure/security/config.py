"""Configuraciones de seguridad según ISO 27001"""

SECURITY_CONFIG = {
    # A.9.4 Control de acceso
    'PASSWORD_MIN_LENGTH': 8,
    'PASSWORD_COMPLEXITY': True,
    'LOGIN_ATTEMPTS_MAX': 3,
    'SESSION_TIMEOUT': 30,  # minutos

    # A.10.1 Controles criptográficos
    'HASH_ALGORITHM': 'pbkdf2:sha256',
    'SALT_LENGTH': 16,

    # A.12.4 Logging
    'LOG_LEVEL': 'INFO',
    'LOG_FORMAT': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    
    # A.13.1 Seguridad de red
    'CSRF_ENABLED': True,
    'SESSION_COOKIE_SECURE': True,
    'SESSION_COOKIE_HTTPONLY': True
}