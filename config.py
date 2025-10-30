import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '../.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-very-secret'
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY') or 'csrf-key-very-secret'
    # Use absolute path to instance/app.db to avoid ambiguity with working directory
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        ('sqlite:///' + os.path.join(basedir, 'instance', 'app.db'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TESTING = os.environ.get('TESTING') or False
    
    # Session Security (ISO 27001 - A.9.4.2, A.18.1.3)
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = int(os.environ.get('SESSION_TIMEOUT', 1800))  # 30 minutes in seconds
    
    # Other settings
    PASSWORD_MIN_LENGTH = 8
    RATE_LIMIT_MAX_REQUESTS = 30
    RATE_LIMIT_WINDOW = 60  # seconds
    AUDIT_LOG_PATH = 'logs/audit.log'
