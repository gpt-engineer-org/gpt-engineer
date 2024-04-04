from email.mime.text import MIMEText
import smtplib

from jinja2 import Environment, PackageLoader, select_autoescape
from .config import settings

env = Environment(
    loader=PackageLoader('app', 'templates'),
    autoescape=select_autoescape(['html', 'xml'])
)

async def send_email(recipient: str, subject: str, body: str):
    message = MIMEText(body, 'html')  # Set subtype to 'html')
    message["From"] = settings.smtp_user
    message["To"] = recipient
    message["Subject"] = subject
    
    # Send Email
    try:
        server = smtplib.SMTP(settings.smtp_host, settings.smtp_port)
        server.starttls()  # Secure the connection
        server.login(settings.smtp_user, settings.smtp_password)
        server.sendmail(settings.smtp_user, recipient, message.as_string())
        print("Email successfully sent!")
    except Exception as e:
        print(f"Failed to send email: {e}")
    finally:
        server.quit()

def render_template(template_name: str, context: dict):
    template = env.get_template(f'{template_name}.html')
    return template.render(context)

if __name__ == '__main__':
    rendered_content = render_template("template1", {"name": "Alex"})
    send_email("topsss1@yandex.ru", "test_letter", rendered_content)
    