import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
import logging
from app.core.config import settings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_email(
    to_email: str,
    subject: str,
    body: str,
    html_body: Optional[str] = None
) -> bool:
    """
    Send email using SMTP configuration from settings.
    """
    try:
        # Check if email configuration is complete
        if not all([settings.SMTP_HOST, settings.SMTP_USER, settings.SMTP_PASSWORD]):
            logger.error("Email configuration incomplete. Please check SMTP settings.")
            return False
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = settings.FROM_EMAIL or settings.SMTP_USER
        msg['To'] = to_email
        
        # Add text part
        text_part = MIMEText(body, 'plain')
        msg.attach(text_part)
        
        # Add HTML part if provided
        if html_body:
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)
        
        # Create secure connection and send email
        context = ssl.create_default_context()
        
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls(context=context)
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"Email sent successfully to {to_email}")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP Authentication failed: {e}")
        return False
    except smtplib.SMTPRecipientsRefused as e:
        logger.error(f"Recipients refused: {e}")
        return False
    except smtplib.SMTPServerDisconnected as e:
        logger.error(f"Server disconnected: {e}")
        return False
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False

def send_verification_email(to_email: str, username: str, verification_token: str) -> bool:
    """
    Send email verification email.
    """
    subject = "Verify your email address"
    # Use your actual domain in production
    base_url = getattr(settings, 'BASE_URL', 'http://localhost:8000')
    verification_url = f"{base_url}/api/v1/auth/verify/{verification_token}"
    
    body = f"""
Hi {username},

Thank you for registering with our application!

Please click the link below to verify your email address:
{verification_url}

If you didn't create an account, please ignore this email.

This verification link will expire in 24 hours.

Best regards,
The Team
    """
    
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; background-color: #f9f9f9; }}
        .button {{ 
            display: inline-block; 
            background-color: #4CAF50; 
            color: white; 
            padding: 14px 20px; 
            text-decoration: none; 
            border-radius: 4px; 
            margin: 20px 0;
        }}
        .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Email Verification</h1>
        </div>
        <div class="content">
            <h2>Hi {username},</h2>
            <p>Thank you for registering with our application!</p>
            <p>Please click the button below to verify your email address:</p>
            <a href="{verification_url}" class="button">Verify Email</a>
            <p>If the button doesn't work, copy and paste this link in your browser:</p>
            <p style="word-break: break-all;">{verification_url}</p>
            <p>If you didn't create an account, please ignore this email.</p>
            <p><strong>This verification link will expire in 24 hours.</strong></p>
        </div>
        <div class="footer">
            <p>Best regards,<br>The Team</p>
        </div>
    </div>
</body>
</html>
    """
    
    return send_email(to_email, subject, body, html_body)

def send_password_reset_email(to_email: str, username: str, reset_token: str) -> bool:
    """
    Send password reset email.
    """
    subject = "Reset your password"
    # Use your actual domain in production
    base_url = getattr(settings, 'BASE_URL', 'http://localhost:3000')
    reset_url = f"{base_url}/reset-password?token={reset_token}"
    
    body = f"""
Hi {username},

You requested to reset your password. Click the link below to reset it:
{reset_url}

This link will expire in 1 hour.

If you didn't request this password reset, please ignore this email. Your password will not be changed.

Best regards,
The Team
    """
    
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #f44336; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; background-color: #f9f9f9; }}
        .button {{ 
            display: inline-block; 
            background-color: #f44336; 
            color: white; 
            padding: 14px 20px; 
            text-decoration: none; 
            border-radius: 4px; 
            margin: 20px 0;
        }}
        .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #666; }}
        .warning {{ background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 4px; margin: 15px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Password Reset</h1>
        </div>
        <div class="content">
            <h2>Hi {username},</h2>
            <p>You requested to reset your password. Click the button below to reset it:</p>
            <a href="{reset_url}" class="button">Reset Password</a>
            <p>If the button doesn't work, copy and paste this link in your browser:</p>
            <p style="word-break: break-all;">{reset_url}</p>
            <div class="warning">
                <p><strong>⚠️ Important:</strong></p>
                <ul>
                    <li>This link will expire in 1 hour</li>
                    <li>If you didn't request this, please ignore this email</li>
                    <li>Your password will not be changed unless you click the link</li>
                </ul>
            </div>
        </div>
        <div class="footer">
            <p>Best regards,<br>The Team</p>
        </div>
    </div>
</body>
</html>
    """
    
    return send_email(to_email, subject, body, html_body)

def send_welcome_email(to_email: str, username: str) -> bool:
    """
    Send welcome email after successful verification.
    """
    subject = "Welcome! Your account is now verified"
    
    body = f"""
Hi {username},

Welcome to our application! Your email has been successfully verified.

You can now access all features of your account.

If you have any questions, please don't hesitate to contact us.

Best regards,
The Team
    """
    
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #2196F3; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; background-color: #f9f9f9; }}
        .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Welcome!</h1>
        </div>
        <div class="content">
            <h2>Hi {username},</h2>
            <p>Welcome to our application! Your email has been successfully verified.</p>
            <p>You can now access all features of your account.</p>
            <p>If you have any questions, please don't hesitate to contact us.</p>
        </div>
        <div class="footer">
            <p>Best regards,<br>The Team</p>
        </div>
    </div>
</body>
</html>
    """
    
    return send_email(to_email, subject, body, html_body)