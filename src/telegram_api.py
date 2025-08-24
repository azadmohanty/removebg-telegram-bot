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
    
    def send_message(self, chat_id: int, text: str, parse_mode: str = "HTML", reply_markup: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """Send a message to a chat with optional inline keyboard"""
        url = f"{self.base_url}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': parse_mode
        }
        
        if reply_markup:
            data['reply_markup'] = reply_markup
        
        try:
            response = requests.post(url, json=data)
            return response.json()
        except Exception as e:
            print(f"Error sending message: {e}")
            return None
    
    def send_photo(self, chat_id: int, photo_data: bytes, caption: str = "", reply_markup: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """Send a photo to a chat with optional inline keyboard"""
        url = f"{self.base_url}/sendPhoto"
        files = {'photo': ('image.png', photo_data, 'image/png')}
        data = {'chat_id': chat_id, 'caption': caption}
        
        if reply_markup:
            data['reply_markup'] = reply_markup
        
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
        
        print(f"TelegramAPI: Getting file info for file_id: {file_id}")
        print(f"TelegramAPI: URL: {url}")
        
        try:
            response = requests.post(url, json=data)
            print(f"TelegramAPI: getFile response status: {response.status_code}")
            result = response.json()
            print(f"TelegramAPI: getFile response: {result}")
            if result.get('ok'):
                return result['result']
            return None
        except Exception as e:
            print(f"Error getting file: {e}")
            return None
    
    def download_file(self, file_path: str) -> Optional[bytes]:
        """Download a file from Telegram"""
        file_url = f"https://api.telegram.org/file/bot{Config.TELEGRAM_BOT_TOKEN}/{file_path}"
        
        print(f"TelegramAPI: Downloading file from: {file_url}")
        
        try:
            response = requests.get(file_url)
            print(f"TelegramAPI: download_file response status: {response.status_code}")
            if response.status_code == 200:
                print(f"TelegramAPI: Downloaded file successfully, size: {len(response.content)} bytes")
                return response.content
            else:
                print(f"TelegramAPI: Failed to download file, status: {response.status_code}")
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
    
    def create_inline_keyboard(self, buttons: list) -> Dict[str, Any]:
        """Create an inline keyboard markup"""
        keyboard = []
        for row in buttons:
            keyboard_row = []
            for button in row:
                keyboard_row.append({
                    'text': button['text'],
                    'callback_data': button['callback_data']
                })
            keyboard.append(keyboard_row)
        
        return {
            'inline_keyboard': keyboard
        }
    
    def answer_callback_query(self, callback_query_id: str, text: str = None, show_alert: bool = False) -> Optional[Dict[str, Any]]:
        """Answer a callback query"""
        url = f"{self.base_url}/answerCallbackQuery"
        data = {
            'callback_query_id': callback_query_id
        }
        
        if text:
            data['text'] = text
        if show_alert:
            data['show_alert'] = show_alert
        
        try:
            response = requests.post(url, json=data)
            return response.json()
        except Exception as e:
            print(f"Error answering callback query: {e}")
            return None

# Global API instance
telegram_api = TelegramAPI()
