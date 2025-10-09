import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import os
from typing import Optional

class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@gptengineer.app")
    
    def send_verification_email(self, new_email: str, token: str, user_id: int):
        """Send verification email to new email address"""
        verification_url = f"https://yourapp.com/verify-email-change/{token}"
        
        subject = "Verify Your New Email Address"
        body = f"""
        Hi there,
        
        You have requested to change your email address to this one.
        
        Please click the link below to verify your new email address:
        {verification_url}
        
        This link will expire in 24 hours.
        
        If you didn't request this change, please ignore this email and contact support.
        
        Best regards,
        GPT Engineer Team
        """
        
        self._send_email(new_email, subject, body)
    
    def send_change_notification_old_email(self, old_email: str, new_email: str):
        """Send notification to old email address"""
        subject = "Important: Your Email Address is Being Changed"
        body = f"""
        Hi there,
        
        This is to notify you that your email address is being changed from {old_email} to {new_email}.
        
        If you didn't make this change, please contact support immediately.
        
        Best regards,
        GPT Engineer Team
        """
        
        self._send_email(old_email, subject, body)
    
    def send_change_notification_new_email(self, new_email: str):
        """Send welcome notification to new email address"""
        subject = "Email Change Successful"
        body = f"""
        Hi there,
        
        Your email address has been successfully updated to {new_email}.
        
        You can now use this email to log into your account.
        
        Best regards,
        GPT Engineer Team
        """
        
        self._send_email(new_email, subject, body)
    
    def _send_email(self, to_email: str, subject: str, body: str):
        """Internal method to send email"""
        try:
            if not all([self.smtp_username, self.smtp_password]):
                print(f"Email not sent (SMTP not configured): {subject} to {to_email}")
                return
            
            msg = MimeMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MimeText(body, 'plain'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            print(f"Email sent: {subject} to {to_email}")
        except Exception as e:
            print(f"Failed to send email to {to_email}: {str(e)}")