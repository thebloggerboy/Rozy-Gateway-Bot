# rozy-gateway-bot/handlers.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler

# config.py से MAIN_CHANNEL_LINK इम्पोर्ट करें (इसे हमें config.py में बनाना होगा)
from config import WORKER_BOT_USERNAME, MAIN_CHANNEL_LINK 
from database import generate_secure_token

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # अगर यूजर लिंक के साथ आया है
    if context.args:
        file_key = context.args[0]
        secure_token = generate_secure_token(file_key, user.id)
        
        if secure_token:
            worker_url = f"https://t.me/{WORKER_BOT_USERNAME}?start={secure_token}"
            keyboard = [[InlineKeyboardButton("Click Here to Get File", url=worker_url)]]
            await update.message.reply_text(
                "Your secure link is ready. It will expire soon. Click below:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await update.message.reply_text("Sorry, could not generate a secure link.")
            
    # अगर यूजर ने सीधे /start भेजा है
    else:
        keyboard = [[InlineKeyboardButton("🚀 Go to Main Channel 🚀", url=MAIN_CHANNEL_LINK)]]
        await update.message.reply_text(
            "Welcome! Please use a link from our main channel to get files.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

def setup_handlers(application):
    application.add_handler(CommandHandler("start", start))
