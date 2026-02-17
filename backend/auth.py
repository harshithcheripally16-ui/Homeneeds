# backend/auth.py
import random
import string
import traceback
import os
from flask_mail import Mail, Message

mail = Mail()


def generate_verification_code():
    return ''.join(random.choices(string.digits, k=6))


def send_verification_email(user_email, code):
    # Log mail configuration status
    username = os.environ.get('MAIL_USERNAME')
    password = os.environ.get('MAIL_PASSWORD')

    print(f"[EMAIL] Attempting to send code to: {user_email}")
    print(f"[EMAIL] Using sender: {username}")
    print(f"[EMAIL] Password configured: {'YES' if password else 'NO'}")

    if not username or not password:
        print(f"[EMAIL] ✗ MAIL_USERNAME or MAIL_PASSWORD not set!")
        print(f"[EMAIL] *** VERIFICATION CODE for {user_email}: {code} ***")
        print(f"[EMAIL] Set these in Render → Environment Variables")
        return False

    try:
        msg = Message(
            subject='Home Needs - Email Verification Code',
            sender=username,
            recipients=[user_email],
            html=f'''
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
        )
        mail.send(msg)
        print(f"[EMAIL] ✓ Email sent successfully to {user_email}")
        return True
    except Exception as e:
        error_msg = str(e)
        print(f"[EMAIL] ✗ Failed to send email")
        print(f"[EMAIL] Error type: {type(e).__name__}")
        print(f"[EMAIL] Error message: {error_msg}")
        print(f"[EMAIL] Full traceback:")
        print(traceback.format_exc())
        print(f"[EMAIL] *** VERIFICATION CODE for {user_email}: {code} ***")

        # Common error explanations
        if 'Authentication' in error_msg or 'auth' in error_msg.lower():
            print(
                f"[EMAIL] HINT: Wrong password. Use Gmail App Password, not regular password")
            print(
                f"[EMAIL] HINT: Get one at https://myaccount.google.com/apppasswords")
        elif 'Connection' in error_msg or 'connect' in error_msg.lower():
            print(
                f"[EMAIL] HINT: Cannot connect to smtp.gmail.com. Check MAIL_SERVER and MAIL_PORT")
        elif 'SSL' in error_msg or 'TLS' in error_msg:
            print(
                f"[EMAIL] HINT: SSL/TLS issue. Check MAIL_USE_TLS=True and MAIL_PORT=587")

        return False
