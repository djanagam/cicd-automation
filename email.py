import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(from_email, to_email, subject, body, smtp_server, smtp_port, smtp_username, smtp_password):
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(from_email, to_email, msg.as_string())
        print('Email sent successfully!')
    except Exception as e:
        print(f'An error occurred: {e}')

# Example usage:
from_email = 'sender@example.com'
to_email = 'recipient@example.com'
subject = 'Test Email'
body = 'Hello, this is a test email.'
smtp_server = 'smtp.example.com'
smtp_port = 587
smtp_username = 'username'
smtp_password = 'password'

send_email(from_email, to_email, subject, body, smtp_server, smtp_port, smtp_username, smtp_password)