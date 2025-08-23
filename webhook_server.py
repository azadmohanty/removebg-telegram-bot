from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application
import os
from dotenv import load_dotenv
import logging

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Global variable to store the bot application
bot_app = None

def set_bot_app(application):
    """Set the bot application for webhook handling"""
    global bot_app
    bot_app = application

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming webhook from Telegram"""
    try:
        if bot_app is None:
            return jsonify({'error': 'Bot not initialized'}), 500
        
        # Get the update from Telegram
        update_data = request.get_json()
        update = Update.de_json(update_data, bot_app.bot)
        
        # Process the update
        bot_app.process_update(update)
        
        return jsonify({'status': 'ok'})
    except Exception as e:
        logging.error(f"Webhook error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'bot_initialized': bot_app is not None})

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

def run_webhook_server(host='0.0.0.0', port=5000, debug=False):
    """Run the webhook server"""
    app.run(host=host, port=port, debug=debug)

