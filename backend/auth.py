# backend/auth.py
import random
import string
import os

from flask_mail import Mail

mail = Mail()

last_codes = {}


def generate_verification_code():
    return ''.join(random.choices(string.digits, k=6))


def send_verification_email(user_email, code):
    """
    Email is not available on Render free tier.
    Just log the code and return False so app auto-verifies.
    """
    last_codes[user_email] = code
    print(f"[EMAIL] Code for {user_email}: {code}")
    print(f"[EMAIL] SMTP not available — user will be auto-verified")
    return False
