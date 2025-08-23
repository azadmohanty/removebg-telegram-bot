<<<<<<< HEAD
# 🤖 Telegram RemoveBG Bot

A Telegram bot that removes the background from uploaded images using the [remove.bg API](https://www.remove.bg/api).

## ✨ Features
- **Background Removal**: Removes background from uploaded photos using remove.bg API
- **Interactive Menu**: User-friendly interface with keyboard shortcuts
- **User Management**: Firebase integration for user analytics and tracking
- **Admin Panel**: Advanced controls for bot administrators
- **Broadcast System**: Send messages to all users
- **Webhook Support**: Real-time updates with optional webhook mode
- **Statistics**: Track user count and bot usage
- **Error Handling**: Comprehensive error handling and logging

## 🛠 Setup

### 1. Clone the repo
```bash
git clone https://github.com/your-username/removebg-telegram-bot.git
cd removebg-telegram-bot
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up environment variables
Create a `.env` file in the project root with your API keys:

```bash
# Create .env file
touch .env
```

Add the following content to your `.env` file:
```env
# Required API Keys
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
REMOVE_BG_API_KEY=your_removebg_api_key_here

# Admin Configuration
ADMIN_USER_ID=your_telegram_user_id_here

# Firebase Configuration (Optional - for user management)
FIREBASE_DATABASE_URL=https://your-project.firebaseio.com/
FIREBASE_SERVICE_ACCOUNT_PATH=path/to/serviceAccountKey.json

# Webhook Configuration (Optional - for production)
USE_WEBHOOK=false
WEBHOOK_URL=https://your-domain.com
SECRET_KEY=your_secret_key_here
```

**Important:** Replace the placeholder values with your actual credentials:
- **TELEGRAM_BOT_TOKEN**: Get from [@BotFather](https://t.me/botfather)
- **REMOVE_BG_API_KEY**: Get from [remove.bg](https://www.remove.bg/api)
- **ADMIN_USER_ID**: Your Telegram user ID (use [@userinfobot](https://t.me/userinfobot))
- **FIREBASE_DATABASE_URL**: Your Firebase project URL (optional)
- **USE_WEBHOOK**: Set to `true` for production, `false` for development

### 4. Run the bot
```bash
python bot.py
```

## 👑 Admin Features

### Commands
- `/stats` - View bot statistics and user count
- `/broadcast` - Send message to all users
- `/users` - List all registered users
- `/help` - Show help menu

### Admin Panel
Access the admin panel through the "Admin Panel" button in the main menu (admin users only).

## 🔥 Firebase Integration

The bot automatically saves user information to Firebase when they start the bot:
- User ID, name, and username
- Registration timestamp
- Total user count tracking

## 🌐 Webhook Mode

For production deployment, enable webhook mode:
1. Set `USE_WEBHOOK=true` in your `.env` file
2. Set `WEBHOOK_URL` to your Vercel domain
3. Deploy to Vercel (instructions below)
4. The bot will use webhooks instead of polling for real-time updates

## 🚀 **Deploy to Vercel**

### **Step 1: Push to GitHub**
```bash
git init
git add .
git commit -m "Initial commit: Telegram Background Remover Bot"
git branch -M main
git remote add origin https://github.com/your-username/removebg-telegram-bot.git
git push -u origin main
```

### **Step 2: Deploy to Vercel**
1. **Install Vercel CLI**: `npm i -g vercel`
2. **Login to Vercel**: `vercel login`
3. **Deploy**: `vercel --prod`
4. **Get your domain** (e.g., `https://your-bot.vercel.app`)

### **Step 3: Configure Webhook**
1. **Update your `.env` file**:
   ```env
   USE_WEBHOOK=true
   WEBHOOK_URL=https://your-bot.vercel.app
   ```
2. **Restart your bot**: `python bot.py`

### **Step 4: Set Telegram Webhook**
Your bot will automatically set the webhook when `USE_WEBHOOK=true`

## 📱 Usage

1. Start the bot with `/start`
2. Choose "Remove Background" from the menu
3. Upload an image
4. Wait for processing
5. Receive the image with background removed
=======
# removebg-telegram-bot
Telegram bot that removes backgrounds using remove.bg API with Firebase integration
>>>>>>> 57ebb1e522239deca160b7cd2f3fb868feb052f8
