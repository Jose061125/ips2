import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '../.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-very-secret'
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY') or 'csrf-key-very-secret'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TESTING = os.environ.get('TESTING') or False
    SESSION_TIMEOUT = 30  # minutes
    PASSWORD_MIN_LENGTH = 8
    RATE_LIMIT_MAX_REQUESTS = 30
    RATE_LIMIT_WINDOW = 60  # seconds
    AUDIT_LOG_PATH = 'logs/audit.log'
