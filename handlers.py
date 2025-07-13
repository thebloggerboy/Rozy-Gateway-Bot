from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler
from config import WORKER_BOT_USERNAME
from database import generate_secure_token

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not context.args:
        await update.message.reply_text("Please use a link from our main channel.")
        return
    
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

def setup_handlers(application):
    application.add_handler(CommandHandler("start", start))