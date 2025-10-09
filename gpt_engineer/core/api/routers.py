# gpt-engineer/gpt_engineer/core/api/routers.py
from flask import Blueprint, request, jsonify
from ...user_service import UserService
from ...email_service import EmailService
from ...database.models import Session  # Import your database session

# Create blueprint
user_bp = Blueprint('user', __name__, url_prefix='/api/user')

# Initialize services
db_session = Session()  # Create database session
email_service = EmailService()  # Create email service
user_service = UserService(db_session, email_service)  # Initialize user service

@user_bp.route('/change-email', methods=['POST'])
def change_email():
    """Request email change"""
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    user_id = data.get('user_id')
    new_email = data.get('new_email')
    current_password = data.get('current_password')
    
    if not all([user_id, new_email]):
        return jsonify({"error": "Missing required fields"}), 400
    
    success, message = user_service.request_email_change(
        user_id, new_email, current_password
    )
    
    if success:
        return jsonify({"message": message}), 200
    else:
        return jsonify({"error": message}), 400

@user_bp.route('/verify-email-change/<token>', methods=['GET'])
def verify_email_change(token):
    """Verify email change"""
    success, message = user_service.verify_email_change(token)
    
    if success:
        return jsonify({"message": message}), 200
    else:
        return jsonify({"error": message}), 400

@user_bp.route('/cancel-email-change', methods=['POST'])
def cancel_email_change():
    """Cancel pending email change"""
    data = request.get_json()
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({"error": "User ID required"}), 400
    
    if user_service.cancel_email_change(user_id):
        return jsonify({"message": "Email change cancelled"}), 200
    else:
        return jsonify({"error": "No pending email change found"}), 400