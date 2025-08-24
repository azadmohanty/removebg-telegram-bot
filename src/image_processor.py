"""
Image processing module for the bot
Handles background removal and image operations
"""
import requests
from typing import Optional
from config import Config
from src.telegram_api import telegram_api

class ImageProcessor:
    """Image processing system for background removal"""
    
    def __init__(self):
        self.api_url = Config.REMOVE_BG_API_URL
        self.api_key = Config.REMOVE_BG_API_KEY
    
    def remove_background(self, image_data: bytes) -> Optional[bytes]:
        """Remove background from image using remove.bg API"""
        try:
            headers = {"X-Api-Key": self.api_key}
            files = {"image_file": image_data}
            
            response = requests.post(self.api_url, headers=headers, files=files)
            
            if response.status_code == 200:
                return response.content
            else:
                print(f"Remove.bg API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error processing image: {e}")
            return None
    
    def process_telegram_image(self, file_id: str, chat_id: int) -> bool:
        """Process image from Telegram and send back result"""
        try:
            # Get file information
            file_info = telegram_api.get_file(file_id)
            if not file_info:
                telegram_api.send_message(chat_id, "❌ Failed to get image file")
                return False
            
            # Download image
            image_data = telegram_api.download_file(file_info['file_path'])
            if not image_data:
                telegram_api.send_message(chat_id, "❌ Failed to download image")
                return False
            
            # Remove background
            processed_image = self.remove_background(image_data)
            if not processed_image:
                telegram_api.send_message(chat_id, "❌ Failed to process image")
                return False
            
            # Send processed image back
            telegram_api.send_photo(chat_id, processed_image, "✅ Background removed successfully!""Created with 💖 by Team A.co")
            return True
            
        except Exception as e:
            print(f"Error processing Telegram image: {e}")
            telegram_api.send_message(chat_id, "❌ Error processing image")
            return False

# Global processor instance
image_processor = ImageProcessor()
