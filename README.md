# 🤖 Telegram Background Remover Bot

A professional Telegram bot that removes backgrounds from images using AI-powered APIs.

## 🚀 Features

- **Background Removal**: Remove backgrounds from images using remove.bg API
- **User Analytics**: Track user interactions and statistics using Firebase REST API
- **Admin Controls**: Admin panel with user management and statistics
- **Webhook Support**: Real-time message processing
- **Firebase Integration**: Seamless user data persistence (no authentication required)
- **Professional Architecture**: Modular, scalable codebase
- **Production Ready**: Deployed on Vercel with 24/7 uptime

## 📁 Project Structure

```
removebg-telegram-bot/
├── api/
│   └── index.py              # Vercel serverless function entry point (all-in-one)
├── requirements.txt          # Python dependencies
├── vercel.json              # Vercel deployment configuration
├── .env.example             # Environment variables template
└── README.md                # Project documentation
```

**Note:** This bot uses a simplified, single-file architecture for maximum reliability and easy deployment on Vercel.

## 🛠 Setup

### 1. Clone the repository
```bash
git clone https://github.com/azadmohanty/removebg-telegram-bot.git
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

# Firebase Configuration (REST API - no authentication required)
FIREBASE_DATABASE_URL=https://removebg-bot-telegram-default-rtdb.firebaseio.com

# Webhook Configuration (for production)
USE_WEBHOOK=true
WEBHOOK_URL=https://your-domain.com/webhook
SECRET_KEY=your_secret_key_here
```

**Important:** Replace the placeholder values with your actual credentials:
- **TELEGRAM_BOT_TOKEN**: Get from [@BotFather](https://t.me/botfather)
- **REMOVE_BG_API_KEY**: Get from [remove.bg](https://www.remove.bg/api)
- **ADMIN_USER_ID**: Your Telegram user ID (use [@userinfobot](https://t.me/userinfobot))

## 👑 Admin Features

### Commands
- `/start` - Show welcome message and admin panel (if admin)
- `/help` - Show help menu
- `/stats` - View bot statistics and user count (admin only)
- `/users` - List all registered users (admin only)
- `/admin` - Show admin control panel with inline keyboard (admin only)

### Admin Notifications
- Automatic notifications when new users join
- Real-time user count updates
- User activity tracking

### Inline Keyboard Interface
- **Beautiful Button Layout**: Admin commands displayed as clickable buttons
- **Easy Navigation**: One-click access to statistics, user lists, and help
- **Back Navigation**: Seamless navigation between different admin panels
- **Mobile Friendly**: Optimized for both desktop and mobile Telegram clients

### User Experience Features
- **Developer Button**: Appears after image processing with contact info and GitHub link
- **Rate Bot Button**: Easy way for users to rate and review the bot
- **Remove Another Button**: Quick access to process more images
- **Smart Help System**: Context-aware help with appropriate back navigation

## 🏗 Architecture

### Simplified Design
- **`api/index.py`**: All-in-one webhook handler with inline functions
- **No external dependencies**: All functionality contained in one file
- **Direct API calls**: Uses `requests` library for all external APIs

### Key Benefits
- ✅ **Maximum Reliability**: No circular import issues or complex dependencies
- ✅ **Easy Deployment**: Single file deployment on Vercel
- ✅ **Easy Debugging**: All code in one place for quick troubleshooting
- ✅ **Fast Execution**: No module loading overhead
- ✅ **Production Ready**: Proven to work reliably on Vercel

## 🔥 Firebase Integration

### How It Works
- **REST API**: Uses Firebase REST API directly (no Admin SDK required)
- **No Authentication**: Works with public Firebase databases
- **Automatic Fallback**: Falls back to in-memory storage if Firebase is unavailable
- **Real-time Updates**: Instant user tracking and analytics

### Benefits
- ✅ **No Setup Complexity**: Works immediately with your Firebase URL
- ✅ **Reliable**: Built-in fallback system ensures bot always works
- ✅ **Scalable**: Can handle thousands of users
- ✅ **Real-time**: Instant user statistics and admin notifications

### Testing Firebase
The bot automatically tests Firebase connection on startup and provides status in admin commands.

## 🚀 Deploy to Vercel

### Step 1: Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit: Professional Telegram Background Remover Bot"
git branch -M main
git remote add origin https://github.com/your-username/removebg-telegram-bot.git
git push -u origin main
```

### Step 2: Deploy to Vercel
1. Go to [vercel.com](https://vercel.com) and sign up/login
2. Click "New Project"
3. Import your GitHub repository
4. Configure environment variables in Vercel dashboard
5. Deploy!

### Step 3: Set up Webhook
After deployment, set the webhook URL:
```bash
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://your-vercel-domain.vercel.app/webhook"}'
```

## 📊 Monitoring

### Health Check
Monitor your bot's health:
```
GET https://your-vercel-domain.vercel.app/health
```

Response:
```json
{
  "status": "healthy",
  "storage_connected": true,
  "total_users": 42,
  "bot_version": "1.0.0",
  "bot_name": "Background Remover Bot"
}
```

## 🔧 Development

### Local Development
For local development, you can run the bot directly:
```bash
python api/index.py
```

### Adding New Features
1. Add new functions directly to `api/index.py`
2. Update environment variables as needed
3. Test thoroughly before deployment
4. Keep the single-file architecture for maximum reliability

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For support, please open an issue on GitHub or contact the development team.

---

**Created with 💖 by Team A.co**
