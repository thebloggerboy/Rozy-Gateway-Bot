# rozy-gateway-bot/main.py
import os
import logging
from threading import Thread
from flask import Flask
from telegram.ext import Application
from dotenv import load_dotenv

# हमारे बनाए हुए मॉड्यूल्स को इम्पोर्ट करें
from handlers import setup_handlers
from config import TOKEN # config.py से टोकन इम्पोर्ट करें

load_dotenv()
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Flask वेब सर्वर ---
app = Flask('')
@app.route('/')
def home():
    return "Rozy Gateway Bot is alive and running!"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()

# --- मुख्य फंक्शन ---
def main():
    if not TOKEN:
        logger.critical("GATEWAY_BOT_TOKEN not set! Bot cannot start.")
        return

    application = Application.builder().token(TOKEN).build()
    
    # सभी हैंडलर्स को handlers.py से रजिस्टर करें
    setup_handlers(application)
    
    # Flask को बैकग्राउंड में चलाएं
    keep_alive()
    logger.info("Rozy Gateway Bot is polling!")
    application.run_polling()

if __name__ == '__main__':
    main()
