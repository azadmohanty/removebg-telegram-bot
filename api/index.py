import os
import sys
from datetime import datetime

from flask import Flask, request, jsonify
import requests

# Allow local imports if ever needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Environment configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
REMOVE_BG_API_KEY = os.getenv("REMOVE_BG_API_KEY")
ADMIN_USER_ID = os.getenv("ADMIN_USER_ID", "6995765141")
FIREBASE_DATABASE_URL = os.getenv("FIREBASE_DATABASE_URL")

app = Flask(__name__)

# --------------- Telegram helpers ---------------

def send_message(chat_id, text, reply_markup=None):
    """Send a message to Telegram"""
    if not TELEGRAM_BOT_TOKEN:
        print("Missing TELEGRAM_BOT_TOKEN")
        return None
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    if reply_markup:
        data["reply_markup"] = reply_markup
    try:
        response = requests.post(url, json=data, timeout=15)
        return response.json()
    except Exception as e:
        print(f"Error sending message: {e}")
        return None


def create_inline_keyboard(rows):
    """
    Create inline keyboard markup.
    rows: list of rows, each row is a list of {'text': str, 'callback_data': str}
    """
    keyboard = []
    for row in rows:
        keyboard_row = []
        for button in row:
            keyboard_row.append({
                "text": button["text"],
                "callback_data": button["callback_data"],
            })
        keyboard.append(keyboard_row)
    return {"inline_keyboard": keyboard}


def get_file(file_id):
    """Get file information from Telegram"""
    if not TELEGRAM_BOT_TOKEN:
        return None
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getFile"
    data = {"file_id": file_id}
    try:
        response = requests.post(url, json=data, timeout=15)
        result = response.json()
        if result.get("ok"):
            return result["result"]
        return None
    except Exception as e:
        print(f"Error getting file: {e}")
        return None


def download_file(file_path):
    """Download a file from Telegram"""
    if not TELEGRAM_BOT_TOKEN:
        return None
    file_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_path}"
    try:
        response = requests.get(file_url, timeout=30)
        if response.status_code == 200:
            return response.content
        return None
    except Exception as e:
        print(f"Error downloading file: {e}")
        return None


def send_photo(chat_id, photo_data, caption="", reply_markup=None):
    """Send a photo to Telegram"""
    if not TELEGRAM_BOT_TOKEN:
        print("Missing TELEGRAM_BOT_TOKEN")
        return None
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    files = {"photo": ("image.png", photo_data, "image/png")}
    data = {
        "chat_id": chat_id,
        "caption": caption,
        "parse_mode": "HTML",
    }
    if reply_markup:
        data["reply_markup"] = reply_markup
    try:
        response = requests.post(url, files=files, data=data, timeout=30)
        return response.json()
    except Exception as e:
        print(f"Error sending photo: {e}")
        return None


def answer_callback_query(callback_query_id, text=None, show_alert=False):
    """Answer a callback query"""
    if not TELEGRAM_BOT_TOKEN:
        return None
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/answerCallbackQuery"
    data = {"callback_query_id": callback_query_id}
    if text is not None:
        data["text"] = text
    if show_alert:
        data["show_alert"] = True
    try:
        response = requests.post(url, json=data, timeout=15)
        return response.json()
    except Exception as e:
        print(f"Error answering callback query: {e}")
        return None


def get_me():
    """Get bot information"""
    if not TELEGRAM_BOT_TOKEN:
        return None
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe"
    try:
        response = requests.get(url, timeout=15)
        result = response.json()
        if result.get("ok"):
            return result["result"]
        return None
    except Exception as e:
        print(f"Error getting bot info: {e}")
        return None


# --------------- remove.bg integration ---------------

def remove_background(image_data):
    """Remove background using remove.bg API"""
    if not REMOVE_BG_API_KEY:
        print("Missing REMOVE_BG_API_KEY")
        return None
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
    except requests.exceptions.Timeout:
        print("Remove.bg API timeout - request took too long")
        return None
    except Exception as e:
        print(f"Error in remove.bg API: {e}")
        return None


# --------------- Storage (Firebase REST or fallback) ---------------

def save_user(user_data):
    """Save user data (simplified)"""
    try:
        if FIREBASE_DATABASE_URL:
            user_id = str(user_data.get("id"))
            url = f"{FIREBASE_DATABASE_URL}/users/{user_id}.json"
            data = {
                "id": user_data.get("id"),
                "first_name": user_data.get("first_name"),
                "username": user_data.get("username"),
                "joined_at": datetime.now().isoformat(),
            }
            response = requests.put(url, json=data, timeout=15)
            return response.status_code == 200
        return True
    except Exception:
        return True


def get_user(user_id):
    """Get user data (simplified)"""
    try:
        if FIREBASE_DATABASE_URL:
            url = f"{FIREBASE_DATABASE_URL}/users/{user_id}.json"
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                return response.json()
        return None
    except Exception:
        return None


def get_all_users():
    """Get all users (simplified)"""
    try:
        if FIREBASE_DATABASE_URL:
            url = f"{FIREBASE_DATABASE_URL}/users.json"
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                return response.json() or {}
        return {}
    except Exception:
        return {}


def get_total_users():
    """Get total user count (simplified)"""
    try:
        if FIREBASE_DATABASE_URL:
            url = f"{FIREBASE_DATABASE_URL}/users.json"
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                data = response.json()
                return len(data) if data else 0
        return 1
    except Exception:
        return 1


def get_storage_status():
    """Get storage status (simplified)"""
    try:
        if FIREBASE_DATABASE_URL:
            response = requests.get(f"{FIREBASE_DATABASE_URL}/.json", timeout=15)
            firebase_connected = response.status_code == 200
        else:
            firebase_connected = False
        return {
            "firebase_connected": firebase_connected,
            "fallback_active": not firebase_connected,
            "storage_type": "Firebase REST API" if firebase_connected else "In-Memory",
            "total_users": get_total_users(),
        }
    except Exception:
        return {
            "firebase_connected": False,
            "fallback_active": True,
            "storage_type": "In-Memory",
            "total_users": 1,
        }


def notify_admin_new_user(user):
    """Notify admin of new user registration"""
    try:
        total_users = get_total_users()
        storage_status = get_storage_status()
        new_user_msg = (
            "🆕 New User Joined! 🆕\n\n"
            f"👤User: {user.get('first_name', 'Unknown')}\n"
            f"📝Username: @{user.get('username', 'no_username')}\n\n"
            f"🆔User ID: {user.get('id')}\n\n"
            f"📊 Total Users: {total_users}\n"
            f"💾 Storage: {storage_status['storage_type']}\n\n"
            f"⏰ Joined: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        send_message(ADMIN_USER_ID, new_user_msg)
    except Exception as e:
        print(f"Failed to notify admin: {e}")


# --------------- Admin text builders ---------------

def get_admin_stats():
    """Get admin statistics text"""
    storage_status = get_storage_status()
    total_users = storage_status["total_users"]
    storage_type = storage_status["storage_type"]
    firebase_status = "✅ Connected" if storage_status["firebase_connected"] else "❌ Disconnected"
    return (
        "📊 <b>Bot Statistics</b>\n\n"
        f"👥 <b>Total Users:</b> {total_users}\n"
        f"💾 <b>Storage:</b> {firebase_status}\n"
        f"🔧 <b>Type:</b> {storage_type}"
    )


def get_admin_users():
    """Get admin users list text"""
    users = get_all_users()
    if users:
        user_list = "\n".join([
            f"• {user_data.get('first_name', 'Unknown')} (@{user_data.get('username', 'no_username')})"
            for _, user_data in users.items()
        ])
        return f"👥 <b>All Users ({len(users)}):</b>\n\n{user_list}"
    else:
        return "👥 <b>No users found</b>"


# --------------- Callback handler ---------------

def handle_callback_query(callback_query):
    """Handle inline keyboard button clicks"""
    try:
        callback_data = callback_query.get("data", "")
        from_user = callback_query.get("from", {}) or {}
        callback_id = callback_query.get("id", "")
        chat_id = from_user.get("id")

        # Only admin can access admin callbacks
        if callback_data.startswith("admin_"):
            if str(chat_id) != str(ADMIN_USER_ID):
                answer_callback_query(callback_id, "❌ You don't have permission to use admin commands!", True)
                return

        if callback_data == "admin_stats":
            response_text = get_admin_stats()
            back_keyboard = create_inline_keyboard([
                [{"text": "🔙 Back to Menu", "callback_data": "admin_back"}]
            ])
            send_message(chat_id, response_text, reply_markup=back_keyboard)

        elif callback_data == "admin_users":
            response_text = get_admin_users()
            back_keyboard = create_inline_keyboard([
                [{"text": "🔙 Back to Menu", "callback_data": "admin_back"}]
            ])
            send_message(chat_id, response_text, reply_markup=back_keyboard)

        elif callback_data == "admin_back":
            response_text = "👑 <b>Admin Control Panel</b>\n\nChoose an option from the menu below:"
            admin_keyboard = create_inline_keyboard([
                [{"text": "📊 Statistics", "callback_data": "admin_stats"},
                 {"text": "👥 Users", "callback_data": "admin_users"}],
                [{"text": "ℹ️ Help", "callback_data": "help"},
                 {"text": "🔄 Refresh", "callback_data": "admin_stats"}]  # refresh -> re-show stats
            ])
            send_message(chat_id, response_text, reply_markup=admin_keyboard)

        elif callback_data == "help":
            # If admin, show admin back button; else, show generic back
            back_button = {"text": "🔙 Back to Menu", "callback_data": "admin_back"} \
                          if str(chat_id) == str(ADMIN_USER_ID) else \
                          {"text": "🔙 Back", "callback_data": "back_to_image"}
            response_text = (
                "ℹ️ Help Menu\n\n"
                "1️⃣ Upload an image\n"
                "2️⃣ I'll process it via remove.bg API\n"
                "3️⃣ You'll get back the image with no background\n\n"
                "💡 <b>Tips for best results:</b>\n"
                "• Use high-quality images\n"
                "• Ensure good lighting\n"
                "• Clear subject separation\n\n"
                "⚠️ Note: Limited by remove.bg API usage"
            )
            back_keyboard = create_inline_keyboard([[back_button]])
            send_message(chat_id, response_text, reply_markup=back_keyboard)

        elif callback_data == "developer_info":
            response_text = (
                "👨💻 <b>Developer Information</b>\n\n"
                "🤖 <b>Bot Name:</b> Background Remover Bot\n"
                "👨💼 <b>Developer:</b> Azad Mohanty\n"
                "📧 <b>Contact:</b> @azadmohanty\n"
                "🌐 GitHub: removebg-telegram-bot\n\n"
                "💡 <b>Features:</b>\n"
                "• AI-powered background removal\n"
                "• Firebase user analytics\n"
                "• Professional admin panel\n"
                "• 24/7 uptime on Vercel\n\n"
                "⭐ Rate this bot if you like it!"
            )
            back_keyboard = create_inline_keyboard([
                [{"text": "🔙 Back", "callback_data": "back_to_image"}]
            ])
            send_message(chat_id, response_text, reply_markup=back_keyboard)

        elif callback_data == "rate_bot":
            response_text = (
                "⭐ <b>Rate Our Bot!</b>\n\n"
                "We'd love to hear your feedback!\n\n"
                "📱 <b>Rate on Telegram:</b>\n"
                "• Send /start to @BotFather\n"
                "• Search for our bot\n"
                "• Give us a rating and review!\n\n"
                "💬 <b>Send Feedback:</b>\n"
                "• Contact: @azadmohanty\n"
                "• GitHub: Open an issue\n\n"
                "🙏 Thank you for using our bot!"
            )
            back_keyboard = create_inline_keyboard([
                [{"text": "🔙 Back", "callback_data": "back_to_image"}]
            ])
            send_message(chat_id, response_text, reply_markup=back_keyboard)

        elif callback_data == "remove_another":
            response_text = (
                "🔄 <b>Remove Another Background</b>\n\n"
                "📸 <b>Upload a new image</b> and I'll remove its background!\n\n"
                "💡 <b>Tips for best results:</b>\n"
                "• Use high-quality images\n"
                "• Ensure good lighting\n"
                "• Clear subject separation"
            )
            back_keyboard = create_inline_keyboard([
                [{"text": "🔙 Back", "callback_data": "back_to_image"}]
            ])
            send_message(chat_id, response_text, reply_markup=back_keyboard)

        elif callback_data == "back_to_image":
            response_text = "📸 <b>Ready for a new image!</b>\n\nUpload an image and I'll remove its background!"
            send_message(chat_id, response_text)

        # Always answer the callback to remove the loading state
        answer_callback_query(callback_id)
    except Exception as e:
        print(f"Error handling callback query: {e}")
        try:
            answer_callback_query(callback_query.get("id", ""), "❌ Error processing request.", True)
        except Exception:
            pass


# --------------- Flask routes ---------------

@app.route("/webhook", methods=["POST"])
def webhook():
    """Handle incoming webhook from Telegram"""
    try:
        update_data = request.get_json()
        if not update_data:
            return jsonify({"error": "No data received"}), 400

        print(f"Received webhook data: {update_data}")

        # CallbackQuery branch
        if "callback_query" in update_data:
            handle_callback_query(update_data["callback_query"])
            return jsonify({"status": "ok"})

        # Message branch
        message = update_data.get("message", {})
        if not message:
            return jsonify({"status": "ignored"})

        chat_id = message.get("chat", {}).get("id")
        text = message.get("text", "")
        user = message.get("from", {}) or {}

        # Save user and notify admin if new
        if user and user.get("id"):
            user_id = str(user.get("id"))
            existing_user = get_user(user_id)
            is_new_user = existing_user is None
            save_user(user)
            if is_new_user and user_id != str(ADMIN_USER_ID):
                notify_admin_new_user(user)

        # Text commands
        if text:
            if text == "/start":
                response_text = (
                    f"👋 Hi {user.get('first_name', 'User')}!\n\n"
                    "🤖 I'm your Background Remover Bot\n"
                    "📸 Upload an image and I'll remove its background\n\n"
                    "Created with 💖 by Team A.co"
                )
                reply_markup = None
                if str(user.get("id")) == str(ADMIN_USER_ID):
                    response_text += "\n\n👑 <b>Admin Control Panel</b>\nChoose an option from the menu below:"
                    reply_markup = create_inline_keyboard([
                        [{"text": "📊 Statistics", "callback_data": "admin_stats"},
                         {"text": "👥 Users", "callback_data": "admin_users"}],
                        [{"text": "ℹ️ Help", "callback_data": "help"},
                         {"text": "🔄 Refresh", "callback_data": "admin_stats"}]
                    ])
                send_message(chat_id, response_text, reply_markup=reply_markup)

            elif text == "/help":
                response_text = (
                    "ℹ️ Help Menu\n\n"
                    "1️⃣ Upload an image\n"
                    "2️⃣ I'll process it via remove.bg API\n"
                    "3️⃣ You'll get back the image with no background\n\n"
                    "⚠️ Note: Limited by remove.bg API usage"
                )
                send_message(chat_id, response_text)

            elif text == "/stats" and str(user.get("id")) == str(ADMIN_USER_ID):
                send_message(chat_id, get_admin_stats())

            elif text == "/users" and str(user.get("id")) == str(ADMIN_USER_ID):
                send_message(chat_id, get_admin_users())

            elif text == "/admin" and str(user.get("id")) == str(ADMIN_USER_ID):
                response_text = "👑 <b>Admin Control Panel</b>\n\nChoose an option from the menu below:"
                admin_keyboard = create_inline_keyboard([
                    [{"text": "📊 Statistics", "callback_data": "admin_stats"},
                     {"text": "👥 Users", "callback_data": "admin_users"}],
                    [{"text": "ℹ️ Help", "callback_data": "help"},
                     {"text": "🔄 Refresh", "callback_data": "admin_stats"}]
                ])
                send_message(chat_id, response_text, reply_markup=admin_keyboard)
            else:
                send_message(chat_id, "📸 Please upload an image to remove its background!")
            return jsonify({"status": "ok"})

        # Photo handling
        if message.get("photo"):
            try:
                photo = message["photo"][-1]  # largest size
                file_id = photo["file_id"]

                send_message(chat_id, "🔄 Processing your image... Please wait.")
                send_message(chat_id, "📁 Step 1/5: Getting file information...")
                file_info = get_file(file_id)
                if not file_info:
                    send_message(chat_id, "❌ Failed to get image file")
                    return jsonify({"status": "ok"})

                send_message(chat_id, "📥 Step 2/5: Downloading image...")
                image_data = download_file(file_info["file_path"])
                if not image_data:
                    send_message(chat_id, "❌ Failed to download image")
                    return jsonify({"status": "ok"})

                send_message(chat_id, "🔧 Step 3/5: Removing background...")
                processed_image = remove_background(image_data)
                if not processed_image:
                    send_message(chat_id, "❌ Failed to process image with remove.bg API")
                    return jsonify({"status": "ok"})

                send_message(chat_id, "⌨️ Step 4/5: Preparing response...")
                developer_keyboard = create_inline_keyboard([
                    [{"text": "👨💻 Developer", "callback_data": "developer_info"},
                     {"text": "⭐ Rate Bot", "callback_data": "rate_bot"}],
                    [{"text": "🔄 Remove Another", "callback_data": "remove_another"},
                     {"text": "ℹ️ Help", "callback_data": "help"}]
                ])

                send_message(chat_id, "📤 Step 5/5: Sending result...")
                result = send_photo(
                    chat_id,
                    processed_image,
                    "✅ Background removed successfully!\n\nWith love from A.co",
                    reply_markup=developer_keyboard
                )
                if result:
                    send_message(chat_id, "✅ <b>Background removal completed successfully!</b> 🎉")
                else:
                    send_message(chat_id, "❌ Failed to send processed image")
            except Exception as e:
                print(f"Error processing photo: {e}")
                send_message(chat_id, f"❌ Error processing image: {str(e)}")
            return jsonify({"status": "ok"})

        # Fallback
        return jsonify({"status": "ok"})
    except Exception as e:
        print(f"Webhook error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    storage_status = get_storage_status()
    return jsonify({
        "status": "healthy",
        "firebase_connected": storage_status["firebase_connected"],
        "fallback_active": storage_status["fallback_active"],
        "storage_type": storage_status["storage_type"],
        "total_users": storage_status["total_users"],
        "bot_version": "1.0.0",
        "bot_name": "Background Remover Bot",
    })


@app.route("/test", methods=["GET"])
def test():
    """Test endpoint to verify bot configuration"""
    try:
        config_status = {
            "bot_token": "✅ Set" if TELEGRAM_BOT_TOKEN else "❌ Missing",
            "remove_bg_key": "✅ Set" if REMOVE_BG_API_KEY else "❌ Missing",
            "admin_id": "✅ Set" if ADMIN_USER_ID else "❌ Missing",
            "firebase_url": "✅ Set" if FIREBASE_DATABASE_URL else "❌ Missing",
        }
        storage_status = get_storage_status()
        bot_info = get_me()
        telegram_status = "✅ Connected" if bot_info else "❌ Failed"
        return jsonify({
            "status": "Bot Test Results",
            "configuration": config_status,
            "storage": storage_status,
            "telegram_api": telegram_status,
            "bot_info": bot_info,
            "timestamp": datetime.now().isoformat(),
        })
    except Exception as e:
        return jsonify({
            "status": "Error",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }), 500


@app.route("/webhook-status", methods=["GET"])
def webhook_status():
    """Check webhook status with Telegram"""
    try:
        if not TELEGRAM_BOT_TOKEN:
            return jsonify({"status": "Error", "error": "Missing TELEGRAM_BOT_TOKEN"}), 400
        webhook_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getWebhookInfo"
        response = requests.get(webhook_url, timeout=15)
        webhook_info = response.json()
        bot_info = get_me()
        return jsonify({
            "status": "Webhook Status Check",
            "webhook_info": webhook_info,
            "bot_info": bot_info,
            "configured_webhook_url": "/webhook",
            "timestamp": datetime.now().isoformat(),
        })
    except Exception as e:
        return jsonify({
            "status": "Error",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }), 500


@app.route("/", methods=["GET"])
def home():
    """Home endpoint"""
    return jsonify({
        "message": "Telegram Bot Webhook Server",
        "status": "running",
        "endpoints": {
            "webhook": "/webhook",
            "health": "/health",
            "test": "/test",
            "webhook-status": "/webhook-status",
        },
    })


# Vercel serverless function entry point for local dev
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "3000")))
