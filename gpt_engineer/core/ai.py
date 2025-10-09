from flask import request, jsonify
import json

class UserAPI:
    def __init__(self, memory):
        self.memory = memory
    
    def handle_email_change_request(self):
        data = request.get_json()
        user_id = data.get('user_id')
        new_email = data.get('new_email')
        current_password = data.get('current_password')  # If you have auth
        
        try:
            user = self.memory.get_user(user_id)
            if not user:
                return jsonify({"error": "User not found"}), 404
            
            # Verify current password if authentication exists
            if hasattr(user, 'verify_password'):
                if not user.verify_password(current_password):
                    return jsonify({"error": "Invalid password"}), 401
            
            user.request_email_change(new_email)
            
            # Save user state (you'll need to implement this)
            self.memory.save_user(user)
            
            # Send verification email (implement this)
            self._send_verification_email(user, new_email)
            
            return jsonify({
                "message": "Verification email sent to new email address"
            }), 200
            
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            return jsonify({"error": "Internal server error"}), 500
    
    def handle_email_verification(self, token: str):
        try:
            user = self.memory.get_user_by_token(token)
            if not user:
                return jsonify({"error": "Invalid or expired token"}), 400
            
            if user.verify_email_change(token):
                self.memory.save_user(user)
                return jsonify({
                    "message": "Email updated successfully"
                }), 200
            else:
                return jsonify({"error": "Invalid or expired token"}), 400
                
        except Exception as e:
            return jsonify({"error": "Internal server error"}), 500
    
    def _send_verification_email(self, user, new_email):
        # Implement email sending logic
        # You can integrate with existing notification system
        verification_url = f"https://yourapp.com/verify-email/{user.email_verification_token}"
        
        email_content = f"""
        Hi there,
        
        You requested to change your email address to this one.
        
        Please click the link below to verify your new email address:
        {verification_url}
        
        This link will expire in 24 hours.
        
        If you didn't request this change, please ignore this email.
        """
        
        # Send email (implement based on your email service)
        print(f"Verification email sent to {new_email}: {email_content}")