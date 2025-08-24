import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify
from datetime import datetime
import requests

# Simple configuration without complex imports
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
REMOVE_BG_API_KEY = os.getenv("REMOVE_BG_API_KEY")
ADMIN_USER_ID = os.getenv("ADMIN_USER_ID", "6995765141")
FIREBASE_DATABASE_URL = os.getenv("FIREBASE_DATABASE_URL")

app = Flask(__name__)

# Simple Telegram API functions
def send_message(chat_id, text, reply_markup=None):
    """Send a message to Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    }
    if reply_markup:
        data['reply_markup'] = reply_markup
    
    try:
        response = requests.post(url, json=data)
        return response.json()
    except Exception as e:
        print(f"Error sending message: {e}")
        return None

def create_inline_keyboard(buttons):
    """Create inline keyboard markup"""
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

def download_file(file_path):
    """Download a file from Telegram"""
    file_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_path}"
    
    try:
        response = requests.get(file_url)
        if response.status_code == 200:
            return response.content
        return None
    except Exception as e:
        print(f"Error downloading file: {e}")
        return None

def send_photo(chat_id, photo_data, caption="", reply_markup=None):
    """Send a photo to Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
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

def remove_background(image_data):
    """Remove background using remove.bg API"""
    try:
        headers = {"X-Api-Key": REMOVE_BG_API_KEY}
        files = {"image_file": image_data}
        api_url = "https://api.remove.bg/v1.0/removebg"
        
        response = requests.post(api_url, headers=headers, files=files, timeout=30)
        
        if response.status_code == 200:
            return response.content
        else:
            print(f"Remove.bg API error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"Error in remove.bg API: {e}")
        return None

def get_me():
    """Get bot information"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe"
    
    try:
        response = requests.get(url)
        result = response.json()
        if result.get('ok'):
            return result['result']
        return None
    except Exception as e:
        print(f"Error getting bot info: {e}")
        return None

def answer_callback_query(callback_query_id, text=None, show_alert=False):
    """Answer a callback query"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/answerCallbackQuery"
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

# Simple storage functions
def save_user(user_data):
    """Save user data (simplified)"""
    try:
        if FIREBASE_DATABASE_URL:
            # Try Firebase
            user_id = str(user_data.get('id'))
            url = f"{FIREBASE_DATABASE_URL}/users/{user_id}.json"
            data = {
                'id': user_data.get('id'),
                'first_name': user_data.get('first_name'),
                'username': user_data.get('username'),
                'joined_at': datetime.now().isoformat()
            }
            response = requests.put(url, json=data)
            return response.status_code == 200
        return True
    except:
        return True

def get_user(user_id):
    """Get user data (simplified)"""
    try:
        if FIREBASE_DATABASE_URL:
            url = f"{FIREBASE_DATABASE_URL}/users/{user_id}.json"
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
        return None
    except:
        return None

def get_total_users():
    """Get total user count (simplified)"""
    try:
        if FIREBASE_DATABASE_URL:
            url = f"{FIREBASE_DATABASE_URL}/users.json"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                return len(data) if data else 0
        return 1
    except:
        return 1

def get_storage_status():
    """Get storage status (simplified)"""
    try:
        if FIREBASE_DATABASE_URL:
            # Test Firebase connection
            response = requests.get(f"{FIREBASE_DATABASE_URL}/.json")
            firebase_connected = response.status_code == 200
        else:
            firebase_connected = False
            
        return {
            'firebase_connected': firebase_connected,
            'fallback_active': not firebase_connected,
            'storage_type': 'Firebase REST API' if firebase_connected else 'In-Memory',
            'total_users': get_total_users()
        }
    except:
        return {
            'firebase_connected': False,
            'fallback_active': True,
            'storage_type': 'In-Memory',
            'total_users': 1
        }

def get_all_users():
    """Get all users (simplified)"""
    try:
        if FIREBASE_DATABASE_URL:
            url = f"{FIREBASE_DATABASE_URL}/users.json"
            response = requests.get(url)
            if response.status_code == 200:
                return response.json() or {}
        return {}
    except:
        return {}

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming webhook from Telegram"""
    try:
        # Get the update from Telegram
        update_data = request.get_json()
        
        if not update_data:
            return jsonify({'error': 'No data received'}), 400
        
        # Debug logging
        print(f"Received webhook data: {update_data}")
        
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
        
        # Debug logging for message type
        if message.get('photo'):
            print(f"Processing photo message from chat {chat_id}")
        elif text:
            print(f"Processing text message: '{text}' from chat {chat_id}")
        
        # Save user to storage and check if new user
        if user:
            user_id = str(user.get('id'))
            # Check if this is a new user
            existing_user = get_user(user_id)
            is_new_user = existing_user is None
            
            # Save user to storage
            save_user(user)
            
            # Only notify admin for NEW users (not admin themselves)
            if is_new_user and user_id != ADMIN_USER_ID:
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
                if str(user.get('id')) == ADMIN_USER_ID:
                    response_text += "\n\n👑 **Admin Control Panel**\nChoose an option from the menu below:"
                    admin_keyboard = create_inline_keyboard([
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
                
                send_message(chat_id, response_text, reply_markup=reply_markup)
            elif text == '/help':
                response_text = (
                    "ℹ️ Help Menu\n\n"
                    "1️⃣ Upload an image\n"
                    "2️⃣ I'll process it via remove.bg API\n"
                    "3️⃣ You'll get back the image with no background\n\n"
                    "⚠️ Note: Limited by remove.bg API usage"
                )
            elif text == '/stats' and str(user.get('id')) == ADMIN_USER_ID:
                storage_status = get_storage_status()
                total_users = storage_status['total_users']
                storage_type = storage_status['storage_type']
                firebase_status = "✅ Connected" if storage_status['firebase_connected'] else "❌ Disconnected"
                
                response_text = (
                    f"📊 **Bot Statistics**\n\n"
                    f"👥 **Total Users:** {total_users}\n"
                    f"💾 **Storage:** {firebase_status}\n"
                    f"🔧 **Type:** {storage_type}"
                )
            elif text == '/users' and str(user.get('id')) == ADMIN_USER_ID:
                response_text = get_admin_users()
                send_message(chat_id, response_text)
                
            elif text == '/admin' and str(user.get('id')) == ADMIN_USER_ID:
                response_text = "👑 **Admin Control Panel**\n\nChoose an option from the menu below:"
                admin_keyboard = create_inline_keyboard([
                    [
                        {'text': '📊 Statistics', 'callback_data': 'admin_stats'},
                        {'text': '👥 Users', 'callback_data': 'admin_users'}
                    ],
                    [
                        {'text': 'ℹ️ Help', 'callback_data': 'help'},
                        {'text': '🔄 Refresh', 'callback_data': 'admin_refresh'}
                    ]
                ])
                send_message(chat_id, response_text, reply_markup=admin_keyboard)
            else:
                response_text = "📸 Please upload an image to remove its background!"
                send_message(chat_id, response_text)
        
        # Handle photo messages
        elif message.get('photo'):
            try:
                photo = message['photo'][-1]  # Get the largest photo
                file_id = photo['file_id']
                
                print(f"Starting image processing for file_id: {file_id}")
                
                # Send initial response to user
                send_message(chat_id, "🔄 Processing your image... Please wait.")
                
                # Get file information
                print(f"Step 1 - Getting file info...")
                file_info = get_file(file_id)
                if not file_info:
                    print(f"Failed to get file info for file_id: {file_id}")
                    send_message(chat_id, "❌ Failed to get image file")
                    return jsonify({'status': 'ok'})
                
                print(f"Got file info: {file_info}")
                
                # Download image
                print(f"Step 2 - Downloading image...")
                image_data = download_file(file_info['file_path'])
                if not image_data:
                    print(f"Failed to download file from path: {file_info['file_path']}")
                    send_message(chat_id, "❌ Failed to download image")
                    return jsonify({'status': 'ok'})
                
                print(f"Downloaded image, size: {len(image_data)} bytes")
                
                # Remove background
                print(f"Step 3 - Sending to remove.bg API...")
                try:
                    processed_image = remove_background(image_data)
                    if not processed_image:
                        print(f"Failed to process image with remove.bg API")
                        send_message(chat_id, "❌ Failed to process image with remove.bg API")
                        return jsonify({'status': 'ok'})
                    print(f"Background removed successfully, processed size: {len(processed_image)} bytes")
                except Exception as e:
                    print(f"Error in remove.bg API call: {e}")
                    send_message(chat_id, f"❌ Error calling remove.bg API: {str(e)}")
                    return jsonify({'status': 'ok'})
                
                # Create developer button keyboard
                print(f"Step 4 - Creating keyboard...")
                try:
                    developer_keyboard = create_inline_keyboard([
                        [
                            {'text': '👨‍💻 Developer', 'callback_data': 'developer_info'},
                            {'text': '⭐ Rate Bot', 'callback_data': 'rate_bot'}
                        ],
                        [
                            {'text': '🔄 Remove Another', 'callback_data': 'remove_another'},
                            {'text': 'ℹ️ Help', 'callback_data': 'help'}
                        ]
                    ])
                    print(f"Keyboard created successfully")
                except Exception as e:
                    print(f"Error creating keyboard: {e}")
                    developer_keyboard = None
                
                # Send processed image back with developer buttons
                print(f"Step 5 - Sending processed image back to chat {chat_id}")
                try:
                    result = send_photo(
                        chat_id, 
                        processed_image, 
                        "✅ Background removed successfully!\n\nWith love from A.co",
                        reply_markup=developer_keyboard
                    )
                    
                    if result:
                        print(f"Image sent successfully to chat {chat_id}")
                    else:
                        print(f"Failed to send image to chat {chat_id}")
                        send_message(chat_id, "❌ Failed to send processed image")
                        
                except Exception as e:
                    print(f"Error sending photo: {e}")
                    send_message(chat_id, f"❌ Error sending processed image: {str(e)}")
                    
            except Exception as e:
                print(f"Error processing photo: {e}")
                send_message(chat_id, f"❌ Error processing image: {str(e)}")
        
        return jsonify({'status': 'ok'})
        
    except Exception as e:
        print(f"Webhook error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

def get_admin_stats():
    """Get admin statistics text"""
    storage_status = get_storage_status()
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
    users = get_all_users()
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
        if str(chat_id) != ADMIN_USER_ID:
            answer_callback_query(
                callback_query.get('id', ''),
                "❌ You don't have permission to use admin commands!",
                show_alert=True
            )
            return
        
        if callback_data == 'admin_stats':
            response_text = get_admin_stats()
            # Add back button
            back_keyboard = create_inline_keyboard([
                [{'text': '🔙 Back to Menu', 'callback_data': 'admin_back'}]
            ])
            send_message(chat_id, response_text, reply_markup=back_keyboard)
            
        elif callback_data == 'admin_users':
            response_text = get_admin_users()
            # Add back button
            back_keyboard = create_inline_keyboard([
                [{'text': '🔙 Back to Menu', 'callback_data': 'admin_back'}]
            ])
            send_message(chat_id, response_text, reply_markup=back_keyboard)
            
        elif callback_data == 'help':
            # Check if user is admin to show appropriate back button
            if str(chat_id) == ADMIN_USER_ID:
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
            back_keyboard = create_inline_keyboard([
                [back_button]
            ])
            send_message(chat_id, response_text, reply_markup=back_keyboard)
            
        elif callback_data == 'admin_refresh':
            response_text = get_admin_stats()
            # Add back button
            back_keyboard = create_inline_keyboard([
                [{'text': '🔙 Back to Menu', 'callback_data': 'admin_back'}]
            ])
            send_message(chat_id, response_text, reply_markup=back_keyboard)
            
        elif callback_data == 'admin_back':
            # Show main admin menu
            response_text = (
                "👑 **Admin Control Panel**\n\n"
                "Choose an option from the menu below:"
            )
            admin_keyboard = create_inline_keyboard([
                [
                    {'text': '📊 Statistics', 'callback_data': 'admin_stats'},
                    {'text': '👥 Users', 'callback_data': 'admin_users'}
                ],
                [
                    {'text': 'ℹ️ Help', 'callback_data': 'help'},
                    {'text': '🔄 Refresh', 'callback_data': 'admin_refresh'}
                ]
            ])
            send_message(chat_id, response_text, reply_markup=admin_keyboard)
            
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
            back_keyboard = create_inline_keyboard([
                [{'text': '🔙 Back', 'callback_data': 'back_to_image'}]
            ])
            send_message(chat_id, response_text, reply_markup=back_keyboard)
            
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
            back_keyboard = create_inline_keyboard([
                [{'text': '🔙 Back', 'callback_data': 'back_to_image'}]
            ])
            send_message(chat_id, response_text, reply_markup=back_keyboard)
            
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
            back_keyboard = create_inline_keyboard([
                [{'text': '🔙 Back', 'callback_data': 'back_to_image'}]
            ])
            send_message(chat_id, response_text, reply_markup=back_keyboard)
            
        elif callback_data == 'back_to_image':
            # This will be handled by the user uploading a new image
            response_text = "📸 **Ready for a new image!**\n\nUpload an image and I'll remove its background!"
            send_message(chat_id, response_text)
        
        # Answer the callback query
        answer_callback_query(callback_query.get('id', ''))
        
    except Exception as e:
        print(f"Error handling callback query: {e}")
        # Try to answer the callback query with an error
        try:
            answer_callback_query(
                callback_query.get('id', ''),
                "❌ An error occurred while processing your request.",
                show_alert=True
            )
        except:
            pass

def notify_admin_new_user(user):
    """Notify admin of new user registration"""
    try:
        total_users = get_total_users()
        storage_status = get_storage_status()
        
        new_user_msg = (
            "🆕 <b>New User Joined!</b> 🆕\n\n"
            f"👤<b>User:</b> <a href='tg://user?id={user.get('id')}'>{user.get('first_name', 'Unknown')}</a>\n"
            f"📝<b>Username:</b> @{user.get('username', 'no_username')}\n\n"
            f"🆔<b>User ID:</b> <code>{user.get('id')}</code>\n\n"
            f"📊 <b>Total Users:</b> {total_users}\n"
            f"💾 <b>Storage:</b> {storage_status['storage_type']}\n\n"
            f"⏰ <b>Joined:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        send_message(ADMIN_USER_ID, new_user_msg)
    except Exception as e:
        print(f"Failed to notify admin: {e}")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    storage_status = get_storage_status()
    return jsonify({
        'status': 'healthy',
        'firebase_connected': storage_status['firebase_connected'],
        'fallback_active': storage_status['fallback_active'],
        'storage_type': storage_status['storage_type'],
        'total_users': storage_status['total_users'],
        'bot_version': Config.BOT_VERSION,
        'bot_name': Config.BOT_NAME
    })

@app.route('/test', methods=['GET'])
def test():
    """Test endpoint to verify bot configuration"""
    try:
        # Test configuration
        config_status = {
            'bot_token': '✅ Set' if TELEGRAM_BOT_TOKEN else '❌ Missing',
            'remove_bg_key': '✅ Set' if REMOVE_BG_API_KEY else '❌ Missing',
            'admin_id': '✅ Set' if ADMIN_USER_ID else '❌ Missing',
            'firebase_url': '✅ Set' if FIREBASE_DATABASE_URL else '❌ Missing'
        }
        
        # Test storage
        storage_status = get_storage_status()
        
        # Test Telegram API
        bot_info = get_me()
        telegram_status = '✅ Connected' if bot_info else '❌ Failed'
        
        return jsonify({
            'status': 'Bot Test Results',
            'configuration': config_status,
            'storage': storage_status,
            'telegram_api': telegram_status,
            'bot_info': bot_info,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'Error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/webhook-status', methods=['GET'])
def webhook_status():
    """Check webhook status with Telegram"""
    try:
        import requests
        
        # Get webhook info from Telegram
        webhook_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getWebhookInfo"
        response = requests.get(webhook_url)
        webhook_info = response.json()
        
        # Get bot info
        bot_info = get_me()
        
        return jsonify({
            'status': 'Webhook Status Check',
            'webhook_info': webhook_info,
            'bot_info': bot_info,
            'configured_webhook_url': Config.WEBHOOK_URL,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'Error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

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

