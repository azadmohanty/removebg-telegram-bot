# 🤖 Telegram Background Remover Bot

A professional Telegram bot that removes backgrounds from images using AI-powered APIs.

## 🚀 Features

- **Background Removal**: Remove backgrounds from images using remove.bg API
- **User Analytics**: Track user interactions and statistics
- **Admin Controls**: Admin panel with user management and statistics
- **Webhook Support**: Real-time message processing
- **Professional Architecture**: Modular, scalable codebase
- **Production Ready**: Deployed on Vercel with 24/7 uptime

## 📁 Project Structure

```
removebg-telegram-bot/
├── api/
│   └── index.py              # Vercel serverless function entry point
├── src/
│   ├── __init__.py           # Package initialization
│   ├── storage.py            # User data storage system
│   ├── telegram_api.py       # Telegram API wrapper
│   └── image_processor.py    # Image processing operations
├── config.py                 # Centralized configuration
├── requirements.txt          # Python dependencies
├── vercel.json              # Vercel deployment configuration
├── .env.example             # Environment variables template
└── README.md                # Project documentation
```

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
- `/stats` - View bot statistics and user count
- `/users` - List all registered users
- `/help` - Show help menu

### Admin Notifications
- Automatic notifications when new users join
- Real-time user count updates
- User activity tracking

## 🏗 Architecture

### Modular Design
- **`config.py`**: Centralized configuration management
- **`src/storage.py`**: User data storage and management
- **`src/telegram_api.py`**: Telegram API interactions
- **`src/image_processor.py`**: Image processing operations
- **`api/index.py`**: Webhook handler for Vercel deployment

### Key Benefits
- ✅ **Separation of Concerns**: Each module has a specific responsibility
- ✅ **Maintainability**: Easy to modify and extend
- ✅ **Testability**: Modular code is easier to test
- ✅ **Scalability**: Can easily add new features
- ✅ **Professional**: Industry-standard project structure

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
For local development, you can run the bot in polling mode:
```bash
python -m src.bot
```

### Adding New Features
1. Create new modules in the `src/` directory
2. Update `config.py` for new configuration options
3. Import and use in `api/index.py`
4. Test thoroughly before deployment

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
