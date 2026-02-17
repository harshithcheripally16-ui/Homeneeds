# backend/config.py
import os


class Config:
    SECRET_KEY = os.environ.get(
        'SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL') or 'sqlite:///home_needs.db'

    # Email — these MUST be set for verification to work
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME')
    MAIL_MAX_EMAILS = None
    MAIL_ASCII_ATTACHMENTS = False

    # Debug mail config on startup
    @staticmethod
    def log_mail_config():
        username = os.environ.get('MAIL_USERNAME')
        password = os.environ.get('MAIL_PASSWORD')
        print(f"[MAIL CONFIG] Server: smtp.gmail.com:587")
        print(f"[MAIL CONFIG] Username: {username}")
        print(f"[MAIL CONFIG] Password set: {'YES' if password else 'NO'}")
        if password:
            print(f"[MAIL CONFIG] Password length: {len(password)}")
        if not username or not password:
            print(
                f"[MAIL CONFIG] ⚠ WARNING: Email will NOT work without both MAIL_USERNAME and MAIL_PASSWORD")


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///home_needs_dev.db'


class ProductionConfig(Config):
    DEBUG = False
    _db_url = os.environ.get('DATABASE_URL', '')
    if _db_url.startswith('postgres://'):
        _db_url = _db_url.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = _db_url or 'sqlite:///home_needs.db'

    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///home_needs_test.db'


config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}
