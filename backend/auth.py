# backend/auth.py
import random
import string
from flask_mail import Mail, Message
import traceback

mail = Mail()


def generate_verification_code():
    return ''.join(random.choices(string.digits, k=6))


def send_verification_email(user_email, code):
    try:
        msg = Message(
            subject='Home Needs - Email Verification Code',
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
        print(f"[EMAIL] ✓ Verification email sent to {user_email}")
        return True
    except Exception as e:
        print(f"[EMAIL] ✗ Failed to send email to {user_email}")
        print(f"[EMAIL] Error: {e}")
        print(f"[EMAIL] Traceback: {traceback.format_exc()}")
        print(f"[EMAIL] *** VERIFICATION CODE for {user_email}: {code} ***")
        return False
