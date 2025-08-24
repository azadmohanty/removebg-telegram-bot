import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify
from datetime import datetime
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
        callback_query = update_data.get('callback_query', {})
        
        if callback_query:
            # Handle callback query (inline keyboard button clicks)
            handle_callback_query(callback_query)
            return jsonify({'status': 'ok'})
        
        chat_id = message.get('chat', {}).get('id')
        text = message.get('text', '')
        user = message.get('from', {})
        
        # Save user to storage and check if new user
        if user:
            user_id = str(user.get('id'))
            # Check if this is a new user
            existing_user = storage.get_user(user_id)
            is_new_user = existing_user is None
            
            # Save user to storage
            storage.save_user(user)
            
            # Only notify admin for NEW users (not admin themselves)
            if is_new_user and user_id != Config.ADMIN_USER_ID:
                notify_admin_new_user(user)
        
        # Handle different types of messages
        if text:
            if text == '/start':
                response_text = (
                    f"👋 Hi {user.get('first_name', 'User')}!\n\n"
                    "🤖 I'm your Background Remover Bot\n"
                    "📸 Upload an image and I'll remove its background\n\n"
                    "Created with 💖 by Team A.co\n\n"
                )
                
                # Add admin keyboard for admin users
                reply_markup = None
                if str(user.get('id')) == Config.ADMIN_USER_ID:
                    response_text += "\n\n👑 **Admin Control Panel**\nChoose an option from the menu below:"
                    admin_keyboard = telegram_api.create_inline_keyboard([
                        [
                            {'text': '📊 Statistics', 'callback_data': 'admin_stats'},
                            {'text': '👥 Users', 'callback_data': 'admin_users'}
                        ],
                        [
                            {'text': 'ℹ️ Help', 'callback_data': 'help'},
                            {'text': '🔄 Refresh', 'callback_data': 'admin_refresh'}
                        ]
                    ])
                    reply_markup = admin_keyboard
                
                telegram_api.send_message(chat_id, response_text, reply_markup=reply_markup)
            elif text == '/help':
                response_text = (
                    "ℹ️ Help Menu\n\n"
                    "1️⃣ Upload an image\n"
                    "2️⃣ I'll process it via remove.bg API\n"
                    "3️⃣ You'll get back the image with no background\n\n"
                    "⚠️ Note: Limited by remove.bg API usage"
                )
            elif text == '/stats' and str(user.get('id')) == Config.ADMIN_USER_ID:
                storage_status = storage.get_storage_status()
                total_users = storage_status['total_users']
                storage_type = storage_status['storage_type']
                firebase_status = "✅ Connected" if storage_status['firebase_connected'] else "❌ Disconnected"
                
                response_text = (
                    f"📊 **Bot Statistics**\n\n"
                    f"👥 **Total Users:** {total_users}\n"
                    f"💾 **Storage:** {firebase_status}\n"
                    f"🔧 **Type:** {storage_type}"
                )
            elif text == '/users' and str(user.get('id')) == Config.ADMIN_USER_ID:
                response_text = get_admin_users()
                telegram_api.send_message(chat_id, response_text)
                
            elif text == '/admin' and str(user.get('id')) == Config.ADMIN_USER_ID:
                response_text = "👑 **Admin Control Panel**\n\nChoose an option from the menu below:"
                admin_keyboard = telegram_api.create_inline_keyboard([
                    [
                        {'text': '📊 Statistics', 'callback_data': 'admin_stats'},
                        {'text': '👥 Users', 'callback_data': 'admin_users'}
                    ],
                    [
                        {'text': 'ℹ️ Help', 'callback_data': 'help'},
                        {'text': '🔄 Refresh', 'callback_data': 'admin_refresh'}
                    ]
                ])
                telegram_api.send_message(chat_id, response_text, reply_markup=admin_keyboard)
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

def get_admin_stats():
    """Get admin statistics text"""
    storage_status = storage.get_storage_status()
    total_users = storage_status['total_users']
    storage_type = storage_status['storage_type']
    firebase_status = "✅ Connected" if storage_status['firebase_connected'] else "❌ Disconnected"
    
    return (
        f"📊 **Bot Statistics**\n\n"
        f"👥 **Total Users:** {total_users}\n"
        f"💾 **Storage:** {firebase_status}\n"
        f"🔧 **Type:** {storage_type}"
    )

def get_admin_users():
    """Get admin users list text"""
    users = storage.get_all_users()
    if users:
        user_list = "\n".join([f"• {user_data.get('first_name', 'Unknown')} (@{user_data.get('username', 'no_username')})" for user_id, user_data in users.items()])
        return f"👥 **All Users ({len(users)}):**\n\n{user_list}"
    else:
        return "👥 **No users found**"

def handle_callback_query(callback_query):
    """Handle inline keyboard button clicks"""
    try:
        callback_data = callback_query.get('data', '')
        user = callback_query.get('from', {})
        chat_id = user.get('id')
        
        # Check if user is admin
        if str(chat_id) != Config.ADMIN_USER_ID:
            telegram_api.answer_callback_query(
                callback_query.get('id', ''),
                "❌ You don't have permission to use admin commands!",
                show_alert=True
            )
            return
        
        if callback_data == 'admin_stats':
            response_text = get_admin_stats()
            # Add back button
            back_keyboard = telegram_api.create_inline_keyboard([
                [{'text': '🔙 Back to Menu', 'callback_data': 'admin_back'}]
            ])
            telegram_api.send_message(chat_id, response_text, reply_markup=back_keyboard)
            
        elif callback_data == 'admin_users':
            response_text = get_admin_users()
            # Add back button
            back_keyboard = telegram_api.create_inline_keyboard([
                [{'text': '🔙 Back to Menu', 'callback_data': 'admin_back'}]
            ])
            telegram_api.send_message(chat_id, response_text, reply_markup=back_keyboard)
            
        elif callback_data == 'help':
            # Check if user is admin to show appropriate back button
            if str(chat_id) == Config.ADMIN_USER_ID:
                back_button = {'text': '🔙 Back to Menu', 'callback_data': 'admin_back'}
            else:
                back_button = {'text': '🔙 Back', 'callback_data': 'back_to_image'}
                
            response_text = (
                "ℹ️ Help Menu\n\n"
                "1️⃣ Upload an image\n"
                "2️⃣ I'll process it via remove.bg API\n"
                "3️⃣ You'll get back the image with no background\n\n"
                "💡 **Tips for best results:**\n"
                "• Use high-quality images\n"
                "• Ensure good lighting\n"
                "• Clear subject separation\n\n"
                "⚠️ Note: Limited by remove.bg API usage"
            )
            # Add appropriate back button
            back_keyboard = telegram_api.create_inline_keyboard([
                [back_button]
            ])
            telegram_api.send_message(chat_id, response_text, reply_markup=back_keyboard)
            
        elif callback_data == 'admin_refresh':
            response_text = get_admin_stats()
            # Add back button
            back_keyboard = telegram_api.create_inline_keyboard([
                [{'text': '🔙 Back to Menu', 'callback_data': 'admin_back'}]
            ])
            telegram_api.send_message(chat_id, response_text, reply_markup=back_keyboard)
            
        elif callback_data == 'admin_back':
            # Show main admin menu
            response_text = (
                "👑 **Admin Control Panel**\n\n"
                "Choose an option from the menu below:"
            )
            admin_keyboard = telegram_api.create_inline_keyboard([
                [
                    {'text': '📊 Statistics', 'callback_data': 'admin_stats'},
                    {'text': '👥 Users', 'callback_data': 'admin_users'}
                ],
                [
                    {'text': 'ℹ️ Help', 'callback_data': 'help'},
                    {'text': '🔄 Refresh', 'callback_data': 'admin_refresh'}
                ]
            ])
            telegram_api.send_message(chat_id, response_text, reply_markup=admin_keyboard)
            
        # Developer and user interaction buttons
        elif callback_data == 'developer_info':
            response_text = (
                "👨‍💻 **Developer Information**\n\n"
                "🤖 **Bot Name:** Background Remover Bot\n"
                "👨‍💼 **Developer:** Azad Mohanty\n"
                "📧 **Contact:** @azadmohanty\n"
                "🌐 **GitHub:** [Project Repository](https://github.com/azadmohanty/removebg-telegram-bot)\n\n"
                "💡 **Features:**\n"
                "• AI-powered background removal\n"
                "• Firebase user analytics\n"
                "• Professional admin panel\n"
                "• 24/7 uptime on Vercel\n\n"
                "⭐ **Rate this bot if you like it!**"
            )
            # Add back button
            back_keyboard = telegram_api.create_inline_keyboard([
                [{'text': '🔙 Back', 'callback_data': 'back_to_image'}]
            ])
            telegram_api.send_message(chat_id, response_text, reply_markup=back_keyboard)
            
        elif callback_data == 'rate_bot':
            response_text = (
                "⭐ **Rate Our Bot!**\n\n"
                "We'd love to hear your feedback!\n\n"
                "📱 **Rate on Telegram:**\n"
                "• Send /start to @BotFather\n"
                "• Search for our bot\n"
                "• Give us a rating and review!\n\n"
                "💬 **Send Feedback:**\n"
                "• Contact: @azadmohanty\n"
                "• GitHub: Open an issue\n\n"
                "🙏 **Thank you for using our bot!**"
            )
            # Add back button
            back_keyboard = telegram_api.create_inline_keyboard([
                [{'text': '🔙 Back', 'callback_data': 'back_to_image'}]
            ])
            telegram_api.send_message(chat_id, response_text, reply_markup=back_keyboard)
            
        elif callback_data == 'remove_another':
            response_text = (
                "🔄 **Remove Another Background**\n\n"
                "📸 **Upload a new image** and I'll remove its background!\n\n"
                "💡 **Tips for best results:**\n"
                "• Use high-quality images\n"
                "• Ensure good lighting\n"
                "• Clear subject separation"
            )
            # Add back button
            back_keyboard = telegram_api.create_inline_keyboard([
                [{'text': '🔙 Back', 'callback_data': 'back_to_image'}]
            ])
            telegram_api.send_message(chat_id, response_text, reply_markup=back_keyboard)
            
        elif callback_data == 'back_to_image':
            # This will be handled by the user uploading a new image
            response_text = "📸 **Ready for a new image!**\n\nUpload an image and I'll remove its background!"
            telegram_api.send_message(chat_id, response_text)
        
        # Answer the callback query
        telegram_api.answer_callback_query(callback_query.get('id', ''))
        
    except Exception as e:
        print(f"Error handling callback query: {e}")
        # Try to answer the callback query with an error
        try:
            telegram_api.answer_callback_query(
                callback_query.get('id', ''),
                "❌ An error occurred while processing your request.",
                show_alert=True
            )
        except:
            pass

def notify_admin_new_user(user):
    """Notify admin of new user registration"""
    try:
        total_users = storage.get_total_users()
        storage_status = storage.get_storage_status()
        
        new_user_msg = (
            "🆕 <b>New User Joined!</b> 🆕\n\n"
            f"👤<b>User:</b> <a href='tg://user?id={user.get('id')}'>{user.get('first_name', 'Unknown')}</a>\n"
            f"📝<b>Username:</b> @{user.get('username', 'no_username')}\n\n"
            f"🆔<b>User ID:</b> <code>{user.get('id')}</code>\n\n"
            f"📊 <b>Total Users:</b> {total_users}\n"
            f"💾 <b>Storage:</b> {storage_status['storage_type']}\n\n"
            f"⏰ <b>Joined:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        telegram_api.send_message(Config.ADMIN_USER_ID, new_user_msg)
    except Exception as e:
        print(f"Failed to notify admin: {e}")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    storage_status = storage.get_storage_status()
    return jsonify({
        'status': 'healthy',
        'firebase_connected': storage_status['firebase_connected'],
        'fallback_active': storage_status['fallback_active'],
        'storage_type': storage_status['storage_type'],
        'total_users': storage_status['total_users'],
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

