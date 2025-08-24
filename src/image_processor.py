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
            
            print(f"ImageProcessor: Calling remove.bg API with key: {self.api_key[:10]}...")
            print(f"ImageProcessor: Image size: {len(image_data)} bytes")
            
            response = requests.post(self.api_url, headers=headers, files=files)
            
            print(f"ImageProcessor: remove.bg API response status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"ImageProcessor: remove.bg API success, response size: {len(response.content)} bytes")
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
            print(f"ImageProcessor: Starting to process file_id: {file_id}")
            
            # Get file information
            file_info = telegram_api.get_file(file_id)
            if not file_info:
                print(f"ImageProcessor: Failed to get file info for file_id: {file_id}")
                telegram_api.send_message(chat_id, "❌ Failed to get image file")
                return False
            
            print(f"ImageProcessor: Got file info: {file_info}")
            
            # Download image
            image_data = telegram_api.download_file(file_info['file_path'])
            if not image_data:
                print(f"ImageProcessor: Failed to download file from path: {file_info['file_path']}")
                telegram_api.send_message(chat_id, "❌ Failed to download image")
                return False
            
            print(f"ImageProcessor: Downloaded image, size: {len(image_data)} bytes")
            
            # Remove background
            print(f"ImageProcessor: Sending to remove.bg API...")
            processed_image = self.remove_background(image_data)
            if not processed_image:
                print(f"ImageProcessor: Failed to process image with remove.bg API")
                telegram_api.send_message(chat_id, "❌ Failed to process image")
                return False
            
            print(f"ImageProcessor: Background removed successfully, processed size: {len(processed_image)} bytes")
            
            # Create developer button keyboard
            developer_keyboard = telegram_api.create_inline_keyboard([
                [
                    {'text': '👨‍💻 Developer', 'callback_data': 'developer_info'},
                    {'text': '⭐ Rate Bot', 'callback_data': 'rate_bot'}
                ],
                [
                    {'text': '🔄 Remove Another', 'callback_data': 'remove_another'},
                    {'text': 'ℹ️ Help', 'callback_data': 'help'}
                ]
            ])
            
            # Send processed image back with developer buttons
            print(f"ImageProcessor: Sending processed image back to chat {chat_id}")
            result = telegram_api.send_photo(
                chat_id, 
                processed_image, 
                "✅ Background removed successfully!\n\nWith love from A.co",
                reply_markup=developer_keyboard
            )
            
            if result:
                print(f"ImageProcessor: Image sent successfully to chat {chat_id}")
            else:
                print(f"ImageProcessor: Failed to send image to chat {chat_id}")
            
            return True
            
        except Exception as e:
            print(f"Error processing Telegram image: {e}")
            telegram_api.send_message(chat_id, "❌ Error processing image")
            return False

# Global processor instance
image_processor = ImageProcessor()
