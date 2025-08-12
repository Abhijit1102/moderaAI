import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    def __init__(self):
        # Cloudinary
        self.CLOUDINARY_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
        self.CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
        self.CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

        # Gemini (example placeholders — replace with your actual env keys)
        self.GEMINI_MODEL = os.getenv("GEMINI_MODEL")
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

        # Brevo (email service)
        self.BREVO_API_KEY = os.getenv("BREVO_API_KEY")

        # Email sender address (example)
        self.EMAIL_SENDER = os.getenv("EMAIL_SENDER", "default@example.com")

        # Webhook secret for validating incoming webhook requests
        self.WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")

# Create a singleton config object
config = Config()
