from flask import Flask
from core.api.routes import user_bp
from core.user_service import UserService
from core.email_service import EmailService

app = Flask(__name__)

# Register blueprints
app.register_blueprint(user_bp)

# Initialize services
email_service = EmailService()
# Initialize your database session here

if __name__ == "__main__":
    app.run(debug=True) 