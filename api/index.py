import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify
from config import Config
from src.storage import storage
from src.telegram_api import telegram_api
from src.image_processor import image_processor

# Initialize configuration
Config.validate()

app = Flask(__name__)

# Initialize storage
storage_ref = storage.initialize()

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
        
        # Save user to storage if available
        if storage_ref and user:
            storage.save_user(user)
            # Notify admin of new user (if not admin themselves)
            if str(user.get('id')) != Config.ADMIN_USER_ID:
                notify_admin_new_user(user)
        
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
            elif text == '/stats' and str(user.get('id')) == Config.ADMIN_USER_ID:
                if storage_ref:
                    total_users = storage.get_total_users()
                    response_text = f"📊 **Bot Statistics**\n\n👥 **Total Users:** {total_users}\n\n💾 **Storage:** ✅ Connected"
                else:
                    response_text = "📊 **Bot Statistics**\n\n❌ **Storage:** Not connected"
            elif text == '/users' and str(user.get('id')) == Config.ADMIN_USER_ID:
                if storage_ref:
                    users = storage.get_all_users()
                    if users:
                        user_list = "\n".join([f"• {user_data.get('first_name', 'Unknown')} (@{user_data.get('username', 'no_username')})" for user_data in users.values()])
                        response_text = f"👥 **All Users ({len(users)}):**\n\n{user_list}"
                    else:
                        response_text = "👥 **No users found**"
                else:
                    response_text = "❌ **Storage:** Not connected"
            else:
                response_text = "📸 Please upload an image to remove its background!"
            
            # Send response
            telegram_api.send_message(chat_id, response_text)
        
        # Handle photo messages
        elif message.get('photo'):
            photo = message['photo'][-1]  # Get the largest photo
            file_id = photo['file_id']
            
            # Process image using the image processor
            image_processor.process_telegram_image(file_id, chat_id)
        
        return jsonify({'status': 'ok'})
        
    except Exception as e:
        print(f"Webhook error: {e}")
        return jsonify({'error': str(e)}), 500

def notify_admin_new_user(user):
    """Notify admin of new user registration"""
    try:
        total_users = storage.get_total_users() if storage_ref else 0
        
        new_user_msg = (
            "➕ <b>New User Notification</b> ➕\n\n"
            f"👤<b>User:</b> <a href='tg://user?id={user.get('id')}'>{user.get('first_name', 'Unknown')}</a>\n\n"
            f"🆔<b>User ID:</b> <code>{user.get('id')}</code>\n\n"
            f"🌝 <b>Total Users Count: {total_users}</b>"
        )
        
        telegram_api.send_message(Config.ADMIN_USER_ID, new_user_msg)
    except Exception as e:
        print(f"Failed to notify admin: {e}")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'storage_connected': storage_ref is not None,
        'total_users': storage.get_total_users() if storage_ref else 0,
        'bot_version': Config.BOT_VERSION,
        'bot_name': Config.BOT_NAME
    })

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

