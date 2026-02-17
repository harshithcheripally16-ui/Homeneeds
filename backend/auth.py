# backend/auth.py
import random
import string
import traceback
import os
import threading
from flask_mail import Mail, Message

mail = Mail()

# Store codes for fallback
last_codes = {}


def generate_verification_code():
    return ''.join(random.choices(string.digits, k=6))


def _send_email_thread(app, msg, user_email, code):
    """Send email in background thread"""
    with app.app_context():
        try:
            mail.send(msg)
            print(f"[EMAIL] ✓ Email sent to {user_email}")
        except Exception as e:
            print(f"[EMAIL] ✗ Background send failed: {e}")
            print(f"[EMAIL] *** CODE for {user_email}: {code} ***")


def send_verification_email(user_email, code):
    """Send verification email without blocking the request"""
    from flask import current_app

    last_codes[user_email] = code

    username = os.environ.get('MAIL_USERNAME')
    password = os.environ.get('MAIL_PASSWORD')

    print(f"[EMAIL] Preparing email for: {user_email}")
    print(f"[EMAIL] Code: {code}")
    print(f"[EMAIL] Sender: {username}")
    print(f"[EMAIL] Password set: {'YES' if password else 'NO'}")

    if not username or not password:
        print(f"[EMAIL] ✗ Credentials missing — skipping email")
        print(f"[EMAIL] *** USE CODE: {code} ***")
        return False

    try:
        msg = Message(
            subject='Home Needs - Email Verification Code',
            sender=username,
            recipients=[user_email]
        )
        msg.html = f'''
        <div style="font-family: Arial, sans-serif; max-width: 500px; margin: 0 auto;
                    padding: 30px; background: linear-gradient(135deg, #ff6b6b, #ee5a24);
                    border-radius: 15px;">
            <h1 style="color: white; text-align: center;">Home Needs</h1>
            <div style="background: white; padding: 30px; border-radius: 10px; text-align: center;">
                <h2 style="color: #333;">Verification Code</h2>
                <p style="color: #666; font-size: 16px;">Your verification code is:</p>
                <div style="background: #f8f9fa; padding: 20px; border-radius: 10px;
                            margin: 20px 0; font-size: 36px; font-weight: bold;
                            letter-spacing: 8px; color: #ee5a24;">
                    {code}
                </div>
                <p style="color: #999; font-size: 14px;">This code expires in 10 minutes.</p>
            </div>
        </div>
        '''
        msg.body = f'Your Home Needs verification code is: {code}'

        # Send in background thread so signup doesn't hang
        app = current_app._get_current_object()
        thread = threading.Thread(
            target=_send_email_thread,
            args=(app, msg, user_email, code)
        )
        thread.daemon = True
        thread.start()

        print(f"[EMAIL] ✓ Email queued in background thread")
        return True

    except Exception as e:
        print(f"[EMAIL] ✗ Failed to prepare email: {e}")
        print(f"[EMAIL] *** FALLBACK CODE: {code} ***")
        return False
