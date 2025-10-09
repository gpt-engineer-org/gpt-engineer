class ProjectConfig:
    def __init__(self):
        self.allow_email_changes = True
        self.email_verification_required = True
        self.email_token_expiry_hours = 24
        
    def validate_email_change_config(self):
        # Add configuration validation
        if not hasattr(self, 'smtp_server') and self.allow_email_changes:
            print("Warning: Email changes enabled but SMTP server not configured")   