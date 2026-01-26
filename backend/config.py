import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration for Flask app"""

    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'False') == 'True'

    # Database
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'backend/database.db')

    # Mailgun settings
    MAILGUN_API_KEY = os.getenv('MAILGUN_API_KEY', '')
    MAILGUN_DOMAIN = os.getenv('MAILGUN_DOMAIN', '')
    FROM_EMAIL = os.getenv('FROM_EMAIL', 'noreply@example.com')

    # Authentication settings
    TOKEN_EXPIRATION_MINUTES = int(os.getenv('TOKEN_EXPIRATION_MINUTES', '15'))
    SESSION_TIMEOUT_DAYS = int(os.getenv('SESSION_TIMEOUT_DAYS', '7'))

    # Base URL
    BASE_URL = os.getenv('BASE_URL', 'http://localhost:5000')

    # Session settings
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'False') == 'True'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = SESSION_TIMEOUT_DAYS * 24 * 60 * 60
