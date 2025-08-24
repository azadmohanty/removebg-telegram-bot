"""
Configuration settings for the Telegram Background Remover Bot
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Centralized configuration class"""
    
    # Bot Configuration
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    REMOVE_BG_API_KEY = os.getenv("REMOVE_BG_API_KEY")
    ADMIN_USER_ID = os.getenv("ADMIN_USER_ID")
    
    # Firebase Configuration
    FIREBASE_DATABASE_URL = os.getenv("FIREBASE_DATABASE_URL")
    
    # Webhook Configuration
    USE_WEBHOOK = os.getenv("USE_WEBHOOK", "true").lower() == "true"
    WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://removebg-telegram-bot.vercel.app/webhook")
    SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key_here")
    
    # Bot Information
    BOT_NAME = "Background Remover Bot"
    BOT_VERSION = "1.0.0"
    BOT_DESCRIPTION = "Remove backgrounds from images using AI"
    
    # API Endpoints
    REMOVE_BG_API_URL = "https://api.remove.bg/v1.0/removebg"
    TELEGRAM_API_BASE = "https://api.telegram.org/bot"
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        required_vars = [
            ("TELEGRAM_BOT_TOKEN", cls.TELEGRAM_BOT_TOKEN),
            ("REMOVE_BG_API_KEY", cls.REMOVE_BG_API_KEY),
        ]
        
        missing = []
        for name, value in required_vars:
            if not value:
                missing.append(name)
        
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
        
        return True
