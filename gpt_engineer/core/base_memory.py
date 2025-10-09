# Add user management with email change functionality
class User:
    def __init__(self, user_id: str, email: str, email_verified: bool = False):
        self.user_id = user_id
        self.email = email
        self.email_verified = email_verified
        self.pending_email = None
        self.email_verification_token = None
        self.token_created_at = None
    
    def request_email_change(self, new_email: str) -> bool:
        # Validate email format
        if not self._is_valid_email(new_email):
            raise ValueError("Invalid email format")
        
        # Check if email is already in use (you'll need to implement this)
        if self._email_exists(new_email):
            raise ValueError("Email already registered")
        
        # Generate verification token
        self.email_verification_token = self._generate_verification_token()
        self.pending_email = new_email
        self.token_created_at = datetime.utcnow()
        
        return True
    
    def verify_email_change(self, token: str) -> bool:
        if (self.email_verification_token == token and 
            self._is_token_valid()):
            
            old_email = self.email
            self.email = self.pending_email
            self.pending_email = None
            self.email_verification_token = None
            self.token_created_at = None
            
            # Send notifications
            self._send_email_change_notifications(old_email, self.email)
            return True
        
        return False
    
    def _is_valid_email(self, email: str) -> bool:
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def _generate_verification_token(self) -> str:
        import secrets
        return secrets.token_urlsafe(32)
    
    def _is_token_valid(self) -> bool:
        if not self.token_created_at:
            return False
        expiry_time = self.token_created_at + timedelta(hours=24)
        return datetime.utcnow() < expiry_time