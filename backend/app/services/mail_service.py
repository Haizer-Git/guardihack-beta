import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from werkzeug.exceptions import InternalServerError, ServiceUnavailable

load_dotenv()

class MailService:
    def __init__(self, app=None):
        self.server = None
        self.port = None
        self.username = None
        self.password = None
        self.sender = None
        if app is not None:
            self.init_app(app)
    def init_app(self, app):
        self.server = app.config.get('SMTP_SERVER')
        self.port = int(app.config.get('SMTP_PORT', 587))
        self.username = app.config.get('SMTP_USERNAME')
        self.password = app.config.get('SMTP_PASSWORD')
        self.sender = app.config.get('MAIL_SENDER')
    def send_email(self, recipient, subject, body):
        if not self.sender or not self.password or not self.server or not self.port or not self.username:
            raise ServiceUnavailable("EMAIL_CONFIGURATION_ERROR|Erreur de configuration du mail.")
        if not recipient or not subject or not body:
            raise InternalServerError("EMAIL_PARAMETERS_MISSING|Paramètres de l'email manquants.")
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.sender
            msg["To"] = recipient
            msg.attach(MIMEText(body, "html"))
            server = smtplib.SMTP(self.server, self.port, timeout=10)
            try:
                server.ehlo()
                server.starttls()
                server.login(self.username, self.password)
                server.sendmail(self.sender, recipient, msg.as_string())
            finally:
                server.quit()
        except Exception as e:
            raise InternalServerError("EMAIL_SEND_ERROR|Erreur lors de l'envoi de l'email.")