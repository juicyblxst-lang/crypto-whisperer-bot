"""
🪙 Crypto Whisperer Bot
A Telegram bot that fetches the current Bitcoin price in USD.
Powered by CoinGecko API.
Deployed on Render.com for 24/7 availability.
"""

import os
import logging
import threading
import requests
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv

# -------- LOAD ENVIRONMENT VARIABLES --------
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("❌ No BOT_TOKEN found! Create a .env file with your token.")

# -------- SETUP LOGGING --------
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# -------- FLASK WEB SERVER (for Render.com health checks) --------
flask_app = Flask(__name__)

@flask_app.route('/')
@flask_app.route('/health')
def health_check():
    return "🪙 Crypto Whisperer Bot is running!", 200

def run_flask():
    """Run the Flask web server in a separate thread."""
    port = int(os.environ.get("PORT", 5000))
    flask_app.run(host="0.0.0.0", port=port)

# -------- TELEGRAM BOT COMMANDS --------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message when /start is issued."""
    await update.message.reply_text(
        "🪙 *Crypto Whisperer Bot*\n\n"
        "I watch Bitcoin so you don't have to.\n"
        "Send /price to get the current BTC price in USD.",
        parse_mode='Markdown'
    )

async def get_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fetch Bitcoin price from CoinGecko API and reply."""
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        price = data['bitcoin']['usd']
        
        await update.message.reply_text(
            f"💰 *Bitcoin Price:*\n**${price:,}** USD",
            parse_mode='Markdown'
        )
    except requests.exceptions.RequestException as e:
        logger.error(f"API error: {e}")
        await update.message.reply_text(
            "❌ Sorry, I couldn't fetch the price right now. Please try again later."
        )

# -------- MAIN BOT FUNCTION --------
def main():
    """Start the Telegram bot."""
    logger.info("🪙 Crypto Whisperer Bot is starting...")
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("price", get_price))
    
    logger.info("✅ Bot is running! Talk to it on Telegram.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

# -------- ENTRY POINT --------
if __name__ == '__main__':
    # Start the Flask web server in a background thread (for Render.com)
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    logger.info("🌐 Flask health check server started on port 5000")
    
    # Start the Telegram bot
    main()
