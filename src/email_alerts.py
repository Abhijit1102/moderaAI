from brevo_python import TransactionalEmailsApi, SendSmtpEmail, ApiClient, Configuration
from src.config import config

BREVO_API_KEY = config.BREVO_API_KEY
EMAIL_SENDER = config.EMAIL_SENDER

configuration = Configuration()
configuration.api_key['api-key'] = BREVO_API_KEY

api_client = ApiClient(configuration)
api_instance = TransactionalEmailsApi(api_client)

def send_alert_email(subject, html_content, to_email):
    email = SendSmtpEmail(
        to=[{"email": to_email}],
        subject=subject,
        html_content=html_content,
        sender={"email": EMAIL_SENDER, "name": "Moderation AI"}
    )
    try:
        response = api_instance.send_transac_email(email)
        return response
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return e
