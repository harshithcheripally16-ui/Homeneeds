# backend/auth.py
import random
import string
import traceback
import os
from flask_mail import Mail, Message

mail = Mail()

# Store last code in memory for debugging (remove in final production)
last_codes = {}


def generate_verification_code():
    return ''.join(random.choices(string.digits, k=6))


def send_verification_email(user_email, code):
    """Send verification email. Returns True if sent, False if failed."""

    # Always store code for fallback
    last_codes[user_email] = code

    username = os.environ.get('MAIL_USERNAME')
    password = os.environ.get('MAIL_PASSWORD')

    print(f"[EMAIL] ─────────────────────────────────────")
    print(f"[EMAIL] Sending verification code to: {user_email}")
    print(f"[EMAIL] Code: {code}")
    print(f"[EMAIL] Sender: {username}")
    print(
        f"[EMAIL] Password set: {'YES (' + str(len(password)) + ' chars)' if password else 'NO'}")

    if not username or not password:
        print(f"[EMAIL] ✗ SKIPPED — MAIL_USERNAME or MAIL_PASSWORD not set")
        print(f"[EMAIL] *** USE CODE: {code} ***")
        print(f"[EMAIL] ─────────────────────────────────────")
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
        # Also set plain text version
        msg.body = f'Your Home Needs verification code is: {code}'

        mail.send(msg)
        print(f"[EMAIL] ✓ SUCCESS — Email sent to {user_email}")
        print(f"[EMAIL] ─────────────────────────────────────")
        return True

    except Exception as e:
        error_msg = str(e)
        print(f"[EMAIL] ✗ FAILED — {type(e).__name__}")
        print(f"[EMAIL] Message: {error_msg}")
        print(f"[EMAIL] *** FALLBACK CODE: {code} ***")

        if 'auth' in error_msg.lower() or 'Authentication' in error_msg:
            print(f"[EMAIL] FIX: Use Gmail App Password, not regular password")
            print(f"[EMAIL] GET: https://myaccount.google.com/apppasswords")
        elif 'connect' in error_msg.lower() or 'Connection' in error_msg:
            print(
                f"[EMAIL] FIX: SMTP connection blocked. Try MAIL_PORT=465 with MAIL_USE_SSL=True")
        elif 'timeout' in error_msg.lower():
            print(
                f"[EMAIL] FIX: SMTP timed out. Render may block port 587. Try port 465")

        print(f"[EMAIL] Full error:")
        print(traceback.format_exc())
        print(f"[EMAIL] ─────────────────────────────────────")
        return False
