import random
import string

def generate_otp(length=6):
    return ''.join(random.choices(string.digits, k=length))

def generate_html_email_body(name, otp):
    return f"""
    <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f9f9f9; padding: 30px; border-radius: 10px; color: #333; max-width: 600px; margin: auto; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
        <h2 style="color: #007bff;">Hi {name},</h2>
        <p style="font-size: 16px; line-height: 1.6;">
            Your One-Time Password (OTP) for <strong>Khata Notebook</strong> is:
        </p>
        <div style="font-size: 28px; font-weight: bold; background-color: #e6f0ff; color: #0056b3; padding: 15px 25px; display: inline-block; border-radius: 8px; letter-spacing: 4px; margin: 10px 0;">
            {otp}
        </div>
        <p style="font-size: 15px; line-height: 1.6;">
            This OTP is valid for <strong>5 minutes</strong>. Please do not share it with anyone.
        </p>
        <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
        <p style="font-size: 14px; color: #666;">
            With regards,<br>
            <strong>Team Khata Notebook</strong>
        </p>
    </div>
    """
