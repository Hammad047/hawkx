import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import os
import logging

logger = logging.getLogger(__name__)

def send_email(subject: str, body: str, config: dict, attachment_path: str = None):
    """
    Send an email using the given SMTP configuration.
    """
    try:
        required_keys = ['sender', 'receiver', 'smtp_server', 'smtp_port', 'password']
        missing_keys = [key for key in required_keys if key not in config]
        if missing_keys:
            raise KeyError(f"Missing email config keys: {missing_keys}")

        msg = MIMEMultipart()
        msg['From'] = config['sender']
        msg['To'] = config['receiver']
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        if attachment_path and os.path.exists(attachment_path):
            part = MIMEBase('application', 'octet-stream')
            with open(attachment_path, 'rb') as file:
                part.set_payload(file.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(attachment_path)}"')
            msg.attach(part)

        server = smtplib.SMTP_SSL(config['smtp_server'], config['smtp_port'])
        server.login(config['sender'], config['password'])
        server.send_message(msg)
        server.quit()

        logger.info(f"📧 Email sent to {config['receiver']} with subject: {subject}")

    except Exception as e:
        logger.error(f"❌ Failed to send email: {e}")
