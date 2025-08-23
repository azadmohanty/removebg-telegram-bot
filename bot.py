import os
import logging
import requests
import asyncio
import threading
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
    CallbackQueryHandler,
)
from dotenv import load_dotenv
from firebase_config import initialize_firebase, save_user_to_firebase, get_total_users, get_all_users
from webhook_server import set_bot_app, run_webhook_server

# ==========================
# CONFIGURATION
# ==========================
load_dotenv()  # Load .env file

# Get API keys from environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
REMOVE_BG_API_KEY = os.getenv("REMOVE_BG_API_KEY")
ADMIN_USER_ID = os.getenv("ADMIN_USER_ID", "6995765141")  # Default admin ID
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://your-domain.com/webhook")
USE_WEBHOOK = os.getenv("USE_WEBHOOK", "false").lower() == "true"

# Check if required environment variables are set
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required. Please set it in your .env file")
if not REMOVE_BG_API_KEY:
    raise ValueError("REMOVE_BG_API_KEY environment variable is required. Please set it in your .env file")

# ==========================
# LOGGING
# ==========================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ==========================
# FIREBASE INITIALIZATION
# ==========================
firebase_ref = initialize_firebase()
if firebase_ref:
    logger.info("Firebase initialized successfully")
else:
    logger.warning("Firebase initialization failed - running without database")

# ==========================
# KEYBOARD MENUS
# ==========================
main_menu = ReplyKeyboardMarkup(
    [["Remove Background"], ["Info", "Help"], ["Stats"]], resize_keyboard=True
)

admin_menu = ReplyKeyboardMarkup(
    [["Remove Background"], ["Info", "Help"], ["Stats"], ["Admin Panel"]], resize_keyboard=True
)

# ==========================
# COMMAND HANDLERS
# ==========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    # Save user to Firebase if available
    if firebase_ref:
        save_user_to_firebase(user)
        total_users = get_total_users()
        logger.info(f"New user {user.id} started. Total users: {total_users}")
        
        # Notify admin of new user
        if str(user.id) != ADMIN_USER_ID:
            await notify_admin_new_user(user, total_users)
    
    # Choose menu based on user role
    menu = admin_menu if str(user.id) == ADMIN_USER_ID else main_menu
    
    welcome_text = (
        f"👋 Hi {user.first_name}!\n\n"
        "🤖 I'm your Background Remover Bot\n"
        "📸 Upload an image and I'll remove its background\n\n"
        "Created with 💖 by Team A.co\n\n"
        "✨ Features:\n"
        "• Background removal\n"
        "• User analytics\n"
        "• Admin controls\n"
        "• Webhook support"
    )
    
    await update.message.reply_text(welcome_text, reply_markup=menu)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = (
        "ℹ️ *Help Menu*\n\n"
        "1️⃣ Click *Remove Background* and upload an image\n"
        "2️⃣ I'll process it via remove.bg API\n"
        "3️⃣ You'll get back the image with no background\n\n"
        "🔧 *Admin Commands:*\n"
        "• `/stats` - View bot statistics\n"
        "• `/broadcast` - Send message to all users\n"
        "• `/users` - List all users\n\n"
        "⚠️ Note: Limited by remove.bg API usage"
    )
    
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /info command"""
    info_text = (
        "📊 *Bot Information*\n\n"
        "🤖 **Background Remover Bot**\n"
        "🔧 Built with Python & python-telegram-bot\n"
        "🔥 Firebase integration for user management\n"
        "🌐 Webhook support for real-time updates\n"
        "👑 Admin panel with analytics\n\n"
        "💡 Each background removal consumes remove.bg API credits"
    )
    
    await update.message.reply_text(info_text, parse_mode="Markdown")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stats command - Admin only"""
    user_id = str(update.effective_user.id)
    
    if user_id != ADMIN_USER_ID:
        await update.message.reply_text("❌ Access denied. Admin only.")
        return
    
    if not firebase_ref:
        await update.message.reply_text("❌ Firebase not available")
        return
    
    total_users = get_total_users()
    stats_text = (
        "📊 *Bot Statistics*\n\n"
        f"👥 **Total Users:** {total_users}\n"
        f"🆔 **Admin ID:** {ADMIN_USER_ID}\n"
        f"🌐 **Webhook:** {'✅ Enabled' if USE_WEBHOOK else '❌ Disabled'}\n"
        f"🔥 **Firebase:** {'✅ Connected' if firebase_ref else '❌ Disconnected'}\n\n"
        "📈 *Recent Activity*\n"
        "• Background removals processed\n"
        "• New user registrations\n"
        "• API usage statistics"
    )
    
    await update.message.reply_text(stats_text, parse_mode="Markdown")

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /broadcast command - Admin only"""
    user_id = str(update.effective_user.id)
    
    if user_id != ADMIN_USER_ID:
        await update.message.reply_text("❌ Access denied. Admin only.")
        return
    
    if not firebase_ref:
        await update.message.reply_text("❌ Firebase not available")
        return
    
    # Store broadcast mode in context
    context.user_data['broadcast_mode'] = True
    
    await update.message.reply_text(
        "📢 *Broadcast Mode Activated*\n\n"
        "Enter the message you want to send to all users:",
        parse_mode="Markdown"
    )

async def users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /users command - Admin only"""
    user_id = str(update.effective_user.id)
    
    if user_id != ADMIN_USER_ID:
        await update.message.reply_text("❌ Access denied. Admin only.")
        return
    
    if not firebase_ref:
        await update.message.reply_text("❌ Firebase not available")
        return
    
    users = get_all_users()
    if not users:
        await update.message.reply_text("❌ No users found")
        return
    
    # Create user list with pagination
    user_list = []
    for user_id, user_data in list(users.items())[:10]:  # Show first 10 users
        name = user_data.get('first_name', 'Unknown')
        username = user_data.get('username', '')
        username_text = f"(@{username})" if username else ""
        user_list.append(f"👤 {name} {username_text} - ID: `{user_id}`")
    
    users_text = (
        "👥 *User List* (First 10)\n\n" + 
        "\n".join(user_list) + 
        f"\n\n📊 **Total Users:** {len(users)}"
    )
    
    await update.message.reply_text(users_text, parse_mode="Markdown")

# ==========================
# MESSAGE HANDLERS
# ==========================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages"""
    text = update.message.text
    user_id = str(update.effective_user.id)
    
    # Check if in broadcast mode
    if context.user_data.get('broadcast_mode') and user_id == ADMIN_USER_ID:
        await handle_broadcast(update, context, text)
        return
    
    if text == "Remove Background":
        await update.message.reply_text("📷 Please upload an image.")
    elif text == "Info":
        await info_command(update, context)
    elif text == "Help":
        await help_command(update, context)
    elif text == "Stats":
        await stats_command(update, context)
    elif text == "Admin Panel" and user_id == ADMIN_USER_ID:
        await show_admin_panel(update, context)
    else:
        await update.message.reply_text("❓ Please choose an option from the menu.")

async def handle_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle broadcast message from admin"""
    if not firebase_ref:
        await update.message.reply_text("❌ Firebase not available")
        context.user_data.pop('broadcast_mode', None)
        return
    
    users = get_all_users()
    if not users:
        await update.message.reply_text("❌ No users found to broadcast")
        context.user_data.pop('broadcast_mode', None)
        return
    
    # Remove broadcast mode
    context.user_data.pop('broadcast_mode', None)
    
    # Send broadcast message
    await update.message.reply_text("📢 Broadcasting message...")
    
    success_count = 0
    fail_count = 0
    
    for user_id in users.keys():
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"📢 *Broadcast Message*\n\n{update.message.text}",
                parse_mode="Markdown"
            )
            success_count += 1
        except Exception as e:
            logger.error(f"Failed to send broadcast to {user_id}: {e}")
            fail_count += 1
    
    await update.message.reply_text(
        f"✅ Broadcast completed!\n\n"
        f"📤 Sent to: {success_count} users\n"
        f"❌ Failed: {fail_count} users"
    )

async def show_admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show admin panel with inline buttons"""
    keyboard = [
        [InlineKeyboardButton("📊 Statistics", callback_data="admin_stats")],
        [InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast")],
        [InlineKeyboardButton("👥 Users", callback_data="admin_users")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="admin_settings")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "👑 *Admin Panel*\n\nChoose an option:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline button callbacks"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "admin_stats":
        await stats_command(update, context)
    elif query.data == "admin_broadcast":
        await broadcast_command(update, context)
    elif query.data == "admin_users":
        await users_command(update, context)
    elif query.data == "admin_settings":
        await query.edit_message_text("⚙️ Settings panel - Coming soon!")

# ==========================
# IMAGE HANDLER
# ==========================
async def remove_bg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle image uploads and remove background"""
    if not update.message.photo:
        await update.message.reply_text("⚠️ Please send an image.")
        return

    photo_file = await update.message.photo[-1].get_file()
    await update.message.reply_text("⏳ Processing your image…")

    # Download image
    img_path = f"input_{update.effective_user.id}.jpg"
    await photo_file.download_to_drive(img_path)

    # Call remove.bg API
    with open(img_path, "rb") as img:
        response = requests.post(
            "https://api.remove.bg/v1.0/removebg",
            files={"image_file": img},
            data={"size": "auto"},
            headers={"X-Api-Key": REMOVE_BG_API_KEY},
        )

    if response.status_code == 200:
        output_path = f"output_{update.effective_user.id}.png"
        with open(output_path, "wb") as out:
            out.write(response.content)
        
        # Send processed image
        await update.message.reply_photo(
            photo=open(output_path, "rb"),
            caption="✅ Background removed successfully!"
        )
        
        # Clean up output file
        os.remove(output_path)
        
        # Log successful processing
        logger.info(f"Background removed for user {update.effective_user.id}")
    else:
        await update.message.reply_text(
            f"❌ Failed to process image. Error: {response.status_code}\n{response.text}"
        )

    # Clean up input file
    os.remove(img_path)

# ==========================
# ADMIN NOTIFICATIONS
# ==========================
async def notify_admin_new_user(user, total_users):
    """Notify admin of new user registration"""
    try:
        new_user_msg = (
            "➕ <b>New User Notification</b> ➕\n\n"
            f"👤<b>User:</b> <a href='tg://user?id={user.id}'>{user.first_name}</a>\n\n"
            f"🆔<b>User ID:</b> <code>{user.id}</code>\n\n"
            f"🌝 <b>Total Users Count: {total_users}</b>"
        )
        
        await bot.send_message(ADMIN_USER_ID, new_user_msg, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Failed to notify admin: {e}")

# ==========================
# MAIN FUNCTION
# ==========================
async def main():
    """Main function to run the bot"""
    # Create bot application
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Store bot app reference for webhook
    set_bot_app(app)

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("info", info_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("broadcast", broadcast_command))
    app.add_handler(CommandHandler("users", users_command))

    # Callback queries (inline buttons)
    app.add_handler(CallbackQueryHandler(handle_callback_query))

    # Menu & text input
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Image input
    app.add_handler(MessageHandler(filters.PHOTO, remove_bg))

    logger.info("Bot started successfully!")

    if USE_WEBHOOK:
        # Set webhook
        webhook_url = f"{WEBHOOK_URL}/webhook"
        await app.bot.set_webhook(url=webhook_url)
        logger.info(f"Webhook set to: {webhook_url}")
        
        # Start webhook server in a separate thread
        server_thread = threading.Thread(
            target=run_webhook_server,
            kwargs={'host': '0.0.0.0', 'port': 5000, 'debug': False}
        )
        server_thread.daemon = True
        server_thread.start()
        logger.info("Webhook server started on port 5000")
        
        # Keep the main thread alive
        while True:
            await asyncio.sleep(1)
    else:
        # Use polling (original method)
        logger.info("Starting bot with polling...")
        await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
