# config.py
import os


class Config:
    SECRET_KEY = os.environ.get(
        'SECRET_KEY') or 'home-needs-secret-key-2024-ultra-secure'
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL') or 'sqlite:///home_needs.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Email Configuration
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get(
        'MAIL_USERNAME') or 'harshithcheripally16@gmail.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'dgnmfqvshbfhsaos'
    MAIL_DEFAULT_SENDER = os.environ.get(
        'MAIL_USERNAME') or 'harshithcheripally16@gmail.com'
