"""
🪙 Crypto Whisperer Bot
A Telegram bot that fetches the current Bitcoin price in USD.
Powered by CoinGecko API.
"""

import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("❌ No BOT_TOKEN found! Create a .env file with your token.")

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

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
        await update.message.reply_text("❌ Sorry, I couldn't fetch the price right now. Please try again later.")

def main():
    """Start the bot."""
    logger.info("🪙 Crypto Whisperer Bot is starting...")
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("price", get_price))
    
    logger.info("✅ Bot is running! Talk to it on Telegram.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
