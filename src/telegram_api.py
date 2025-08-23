"""
Telegram API module for the bot
Handles all Telegram API interactions
"""
import requests
from typing import Dict, Any, Optional
from config import Config

class TelegramAPI:
    """Telegram API wrapper for bot operations"""
    
    def __init__(self):
        self.base_url = f"{Config.TELEGRAM_API_BASE}{Config.TELEGRAM_BOT_TOKEN}"
    
    def send_message(self, chat_id: int, text: str, parse_mode: str = "HTML") -> Optional[Dict[str, Any]]:
        """Send a message to a chat"""
        url = f"{self.base_url}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': parse_mode
        }
        
        try:
            response = requests.post(url, json=data)
            return response.json()
        except Exception as e:
            print(f"Error sending message: {e}")
            return None
    
    def send_photo(self, chat_id: int, photo_data: bytes, caption: str = "") -> Optional[Dict[str, Any]]:
        """Send a photo to a chat"""
        url = f"{self.base_url}/sendPhoto"
        files = {'photo': ('image.png', photo_data, 'image/png')}
        data = {'chat_id': chat_id, 'caption': caption}
        
        try:
            response = requests.post(url, files=files, data=data)
            return response.json()
        except Exception as e:
            print(f"Error sending photo: {e}")
            return None
    
    def get_file(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get file information from Telegram"""
        url = f"{self.base_url}/getFile"
        data = {'file_id': file_id}
        
        try:
            response = requests.post(url, json=data)
            result = response.json()
            if result.get('ok'):
                return result['result']
            return None
        except Exception as e:
            print(f"Error getting file: {e}")
            return None
    
    def download_file(self, file_path: str) -> Optional[bytes]:
        """Download a file from Telegram"""
        file_url = f"https://api.telegram.org/file/bot{Config.TELEGRAM_BOT_TOKEN}/{file_path}"
        
        try:
            response = requests.get(file_url)
            if response.status_code == 200:
                return response.content
            return None
        except Exception as e:
            print(f"Error downloading file: {e}")
            return None
    
    def get_me(self) -> Optional[Dict[str, Any]]:
        """Get bot information"""
        url = f"{self.base_url}/getMe"
        
        try:
            response = requests.get(url)
            result = response.json()
            if result.get('ok'):
                return result['result']
            return None
        except Exception as e:
            print(f"Error getting bot info: {e}")
            return None

# Global API instance
telegram_api = TelegramAPI()
