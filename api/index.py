import os
import json
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from firebase_config import initialize_firebase, save_user_to_firebase, get_total_users, get_all_users

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Bot configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
REMOVE_BG_API_KEY = os.getenv("REMOVE_BG_API_KEY")
ADMIN_USER_ID = os.getenv("ADMIN_USER_ID", "6995765141")

# Initialize Firebase
firebase_ref = initialize_firebase()

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming webhook from Telegram"""
    try:
        # Get the update from Telegram
        update_data = request.get_json()
        
        if not update_data:
            return jsonify({'error': 'No data received'}), 400
        
        # Extract message information
        message = update_data.get('message', {})
        chat_id = message.get('chat', {}).get('id')
        text = message.get('text', '')
        user = message.get('from', {})
        
        # Save user to Firebase if available
        if firebase_ref and user:
            save_user_to_firebase(user)
        
        # Handle different types of messages
        if text:
            if text == '/start':
                response_text = (
                    f"👋 Hi {user.get('first_name', 'User')}!\n\n"
                    "🤖 I'm your Background Remover Bot\n"
                    "📸 Upload an image and I'll remove its background\n\n"
                    "Created with 💖 by Team A.co\n\n"
                    "✨ Features:\n"
                    "• Background removal\n"
                    "• User analytics\n"
                    "• Admin controls\n"
                    "• Webhook support"
                )
            elif text == '/help':
                response_text = (
                    "ℹ️ Help Menu\n\n"
                    "1️⃣ Upload an image\n"
                    "2️⃣ I'll process it via remove.bg API\n"
                    "3️⃣ You'll get back the image with no background\n\n"
                    "⚠️ Note: Limited by remove.bg API usage"
                )
            elif text == '/stats' and str(user.get('id')) == ADMIN_USER_ID:
                if firebase_ref:
                    total_users = get_total_users()
                    response_text = f"📊 **Bot Statistics**\n\n👥 **Total Users:** {total_users}\n\n🔥 **Firebase:** ✅ Connected"
                else:
                    response_text = "📊 **Bot Statistics**\n\n❌ **Firebase:** Not connected"
            elif text == '/users' and str(user.get('id')) == ADMIN_USER_ID:
                if firebase_ref:
                    users = get_all_users()
                    if users:
                        user_list = "\n".join([f"• {user_data.get('first_name', 'Unknown')} (@{user_data.get('username', 'no_username')})" for user_data in users.values()])
                        response_text = f"👥 **All Users ({len(users)}):**\n\n{user_list}"
                    else:
                        response_text = "👥 **No users found**"
                else:
                    response_text = "❌ **Firebase:** Not connected"
            else:
                response_text = "📸 Please upload an image to remove its background!"
            
            # Send response
            send_message(chat_id, response_text)
        
        # Handle photo messages
        elif message.get('photo'):
            photo = message['photo'][-1]  # Get the largest photo
            file_id = photo['file_id']
            
            # Get file path
            file_info = get_file(file_id)
            if file_info:
                file_path = file_info['file_path']
                # Download and process image
                process_image(chat_id, file_path)
            else:
                send_message(chat_id, "❌ Failed to get image file")
        
        return jsonify({'status': 'ok'})
        
    except Exception as e:
        print(f"Webhook error: {e}")
        return jsonify({'error': str(e)}), 500

def send_message(chat_id, text):
    """Send a message to a chat"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    }
    try:
        response = requests.post(url, json=data)
        return response.json()
    except Exception as e:
        print(f"Error sending message: {e}")
        return None

def get_file(file_id):
    """Get file information from Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getFile"
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

def process_image(chat_id, file_path):
    """Process image with remove.bg API"""
    try:
        # Download image from Telegram
        file_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_path}"
        image_response = requests.get(file_url)
        
        if image_response.status_code != 200:
            send_message(chat_id, "❌ Failed to download image")
            return
        
        # Send to remove.bg API
        remove_bg_url = "https://api.remove.bg/v1.0/removebg"
        headers = {"X-Api-Key": REMOVE_BG_API_KEY}
        files = {"image_file": image_response.content}
        
        response = requests.post(remove_bg_url, headers=headers, files=files)
        
        if response.status_code == 200:
            # Send processed image back
            send_photo(chat_id, response.content, "✅ Background removed successfully!")
        else:
            send_message(chat_id, f"❌ Failed to process image. Error: {response.status_code}")
            
    except Exception as e:
        print(f"Error processing image: {e}")
        send_message(chat_id, "❌ Error processing image")

def send_photo(chat_id, photo_data, caption=""):
    """Send a photo to a chat"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    files = {'photo': ('image.png', photo_data, 'image/png')}
    data = {'chat_id': chat_id, 'caption': caption}
    
    try:
        response = requests.post(url, files=files, data=data)
        return response.json()
    except Exception as e:
        print(f"Error sending photo: {e}")
        return None

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})

@app.route('/', methods=['GET'])
def home():
    """Home endpoint"""
    return jsonify({
        'message': 'Telegram Bot Webhook Server',
        'status': 'running',
        'endpoints': {
            'webhook': '/webhook',
            'health': '/health'
        }
    })

# Vercel serverless function entry point
if __name__ == "__main__":
    app.run()

