import re
import secrets
from datetime import datetime, timedelta
from typing import Optional, Tuple
from .database.models import User, EmailChangeLog

class UserService:
    def __init__(self, db_session, email_service):
        self.db = db_session
        self.email_service = email_service
    
    def request_email_change(self, user_id: int, new_email: str, current_password: str) -> Tuple[bool, str]:
        """Initiate email change process"""
        try:
            # Get user
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return False, "User not found"
            
            # Verify current password (if applicable)
            if hasattr(user, 'verify_password'):
                if not user.verify_password(current_password):
                    return False, "Current password is incorrect"
            
            # Validate new email format
            if not self._is_valid_email(new_email):
                return False, "Invalid email format"
            
            # Check if new email is same as current
            if user.email.lower() == new_email.lower():
                return False, "New email cannot be the same as current email"
            
            # Check if email already exists
            existing_user = self.db.query(User).filter(User.email == new_email).first()
            if existing_user and existing_user.id != user_id:
                return False, "Email already registered"
            
            # Generate verification token
            token = secrets.token_urlsafe(32)
            
            # Update user record
            user.pending_email = new_email
            user.email_verification_token = token
            user.token_created_at = datetime.utcnow()
            
            # Log the email change request
            change_log = EmailChangeLog(
                user_id=user_id,
                old_email=user.email,
                new_email=new_email,
                status="pending"
            )
            self.db.add(change_log)
            self.db.commit()
            
            # Send verification email
            self.email_service.send_verification_email(new_email, token, user_id)
            
            # Send notification to old email
            self.email_service.send_change_notification_old_email(user.email, new_email)
            
            return True, "Verification email sent to your new email address"
            
        except Exception as e:
            self.db.rollback()
            return False, f"Error: {str(e)}"
    
    def verify_email_change(self, token: str) -> Tuple[bool, str]:
        """Verify and complete email change"""
        try:
            user = self.db.query(User).filter(
                User.email_verification_token == token
            ).first()
            
            if not user:
                return False, "Invalid or expired verification token"
            
            # Check token expiration (24 hours)
            if not user.token_created_at or \
               datetime.utcnow() > user.token_created_at + timedelta(hours=24):
                return False, "Verification token has expired"
            
            if not user.pending_email:
                return False, "No pending email change found"
            
            # Update user email
            old_email = user.email
            user.email = user.pending_email
            user.pending_email = None
            user.email_verification_token = None
            user.token_created_at = None
            user.email_verified = True
            
            # Update email change log
            change_log = self.db.query(EmailChangeLog).filter(
                EmailChangeLog.user_id == user.id,
                EmailChangeLog.new_email == user.email,
                EmailChangeLog.status == "pending"
            ).first()
            
            if change_log:
                change_log.status = "verified"
                change_log.verified_at = datetime.utcnow()
            
            self.db.commit()
            
            # Send success notification to new email
            self.email_service.send_change_notification_new_email(user.email)
            
            return True, "Email updated successfully"
            
        except Exception as e:
            self.db.rollback()
            return False, f"Error: {str(e)}"
    
    def cancel_email_change(self, user_id: int) -> bool:
        """Cancel pending email change"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if user and user.pending_email:
                user.pending_email = None
                user.email_verification_token = None
                user.token_created_at = None
                self.db.commit()
                return True
            return False
        except Exception:
            self.db.rollback()
            return False
    
    def _is_valid_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def cleanup_expired_tokens(self):
        """Clean up expired verification tokens"""
        try:
            expiry_time = datetime.utcnow() - timedelta(hours=24)
            
            # Find users with expired tokens
            expired_users = self.db.query(User).filter(
                User.token_created_at < expiry_time,
                User.pending_email.isnot(None)
            ).all()
            
            for user in expired_users:
                user.pending_email = None
                user.email_verification_token = None
                user.token_created_at = None
            
            self.db.commit()
            print(f"Cleaned up {len(expired_users)} expired tokens")
            
        except Exception as e:
            print(f"Error cleaning up tokens: {str(e)}")