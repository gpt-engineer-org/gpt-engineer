import smtplib
from email.mime.text import MIMEText

# Email settings
smtp_host = 'smtp.gmail.com'
smtp_port = 587
smtp_user = 'a.ermolaev86@gmail.com'
smtp_password = 'hssc xbvu nzae kbcp'

# Email content
sender_email = 'a.ermolaev86@gmail.com'  # Your email
receiver_email = 'topsss1@yandex.ru'  # Receiver's email
subject = 'Hello from Python'
body = '<h1>This is a test email sent from a Python script.</h1>'
body = """
<!DOCTYPE html>
<html>
<head>
    <title>Welcome</title>
</head>
<body>
    <h1>Welcome KAKA!</h1>
    <p>We're glad to have you with us.</p>
</body>
</html>
"""

# Setup MIME
message = MIMEText(body, 'html')  # Set subtype to 'html'
message['From'] = sender_email
message['To'] = receiver_email
message['Subject'] = subject

# Send Email
try:
    server = smtplib.SMTP(smtp_host, smtp_port)
    server.starttls()  # Secure the connection
    server.login(smtp_user, smtp_password)
    server.sendmail(sender_email, receiver_email, message.as_string())
    print("Email successfully sent!")
except Exception as e:
    print(f"Failed to send email: {e}")
finally:
    server.quit()
