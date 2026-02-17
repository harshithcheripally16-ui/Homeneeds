# backend/auth.py
import random
import string
import traceback
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask_mail import Mail

mail = Mail()

# Store codes for fallback
last_codes = {}


def generate_verification_code():
    return ''.join(random.choices(string.digits, k=6))


def send_verification_email(user_email, code):
    """
    Send verification email using direct SMTP (not Flask-Mail).
    This gives us full control over timeouts and error handling.
    """
    last_codes[user_email] = code

    username = os.environ.get('MAIL_USERNAME')
    password = os.environ.get('MAIL_PASSWORD')
    smtp_server = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.environ.get('MAIL_PORT', 587))

    print(f"[EMAIL] ─────────────────────────────────────")
    print(f"[EMAIL] To:       {user_email}")
    print(f"[EMAIL] From:     {username}")
    print(f"[EMAIL] Server:   {smtp_server}:{smtp_port}")
    print(
        f"[EMAIL] Password: {'SET (' + str(len(password)) + ' chars)' if password else 'NOT SET'}")
    print(f"[EMAIL] Code:     {code}")

    if not username or not password:
        print(f"[EMAIL] ✗ Credentials missing")
        print(f"[EMAIL] ─────────────────────────────────────")
        return False

    # Build email
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Home Needs - Email Verification Code'
    msg['From'] = username
    msg['To'] = user_email

    text_body = f'Your Home Needs verification code is: {code}'

    html_body = f'''
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

    msg.attach(MIMEText(text_body, 'plain'))
    msg.attach(MIMEText(html_body, 'html'))

    # Try sending with multiple methods
    # Method 1: TLS on port 587
    if smtp_port == 587:
        try:
            print(f"[EMAIL] Trying TLS on port 587...")
            server = smtplib.SMTP(smtp_server, 587, timeout=15)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(username, password)
            server.sendmail(username, user_email, msg.as_string())
            server.quit()
            print(f"[EMAIL] ✓ SUCCESS via TLS:587")
            print(f"[EMAIL] ─────────────────────────────────────")
            return True
        except Exception as e:
            print(f"[EMAIL] ✗ TLS:587 failed: {type(e).__name__}: {e}")

    # Method 2: SSL on port 465
    try:
        print(f"[EMAIL] Trying SSL on port 465...")
        server = smtplib.SMTP_SSL(smtp_server, 465, timeout=15)
        server.ehlo()
        server.login(username, password)
        server.sendmail(username, user_email, msg.as_string())
        server.quit()
        print(f"[EMAIL] ✓ SUCCESS via SSL:465")
        print(f"[EMAIL] ─────────────────────────────────────")
        return True
    except Exception as e:
        print(f"[EMAIL] ✗ SSL:465 failed: {type(e).__name__}: {e}")

    # Method 3: TLS on port 587 (retry if we started with 465)
    if smtp_port != 587:
        try:
            print(f"[EMAIL] Trying TLS on port 587 (fallback)...")
            server = smtplib.SMTP(smtp_server, 587, timeout=15)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(username, password)
            server.sendmail(username, user_email, msg.as_string())
            server.quit()
            print(f"[EMAIL] ✓ SUCCESS via TLS:587 (fallback)")
            print(f"[EMAIL] ─────────────────────────────────────")
            return True
        except Exception as e:
            print(
                f"[EMAIL] ✗ TLS:587 fallback failed: {type(e).__name__}: {e}")

    # All methods failed
    print(f"[EMAIL] ✗ ALL METHODS FAILED")
    print(f"[EMAIL] *** CODE for {user_email}: {code} ***")
    print(f"[EMAIL] ─────────────────────────────────────")
    return False
