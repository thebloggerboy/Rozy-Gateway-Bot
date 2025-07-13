import os, logging
from threading import Thread
from flask import Flask
from telegram.ext import Application
from dotenv import load_dotenv
from handlers import setup_handlers

load_dotenv()
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
TOKEN = os.environ.get("GATEWAY_BOT_TOKEN")

app = Flask('')
@app.route('/')
def home(): return "Rozy Gateway Bot is alive!"
def run_flask(): app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
def keep_alive(): Thread(target=run_flask).start()

def main():
    if not TOKEN: logging.critical("GATEWAY_BOT_TOKEN not set!"); return
    application = Application.builder().token(TOKEN).build()
    setup_handlers(application)
    keep_alive()
    logging.info("Rozy Gateway Bot is polling!")
    application.run_polling()

if __name__ == '__main__':
    main()
