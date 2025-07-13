# rozy-gateway-bot/handlers.py
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from telegram.constants import ParseMode
from telegram.error import BadRequest

from config import WORKER_BOT_USERNAME, ADMIN_IDS, FORCE_SUB_CHANNELS, MAIN_CHANNEL_LINK
from database import generate_secure_token, add_user, get_all_user_ids, db, save_db

logger = logging.getLogger(__name__)

# --- हेल्पर फंक्शन्स ---
async def is_user_member(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    if user_id in ADMIN_IDS: return True
    for channel in FORCE_SUB_CHANNELS:
        try:
            member = await context.bot.get_chat_member(chat_id=channel["chat_id"], user_id=user_id)
            if member.status not in ['member', 'administrator', 'creator']: return False
        except BadRequest: return False
    return True

async def send_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE, file_key: str):
    join_buttons = [InlineKeyboardButton(ch["name"], url=ch["invite_link"]) for ch in FORCE_SUB_CHANNELS]
    keyboard = [join_buttons, [InlineKeyboardButton("✅ Joined", callback_data=f"check_{file_key}")]]
    await update.message.reply_text("Please join our channels first to get the download link.", reply_markup=InlineKeyboardMarkup(keyboard))

async def send_download_options(chat_id: int, context: ContextTypes.DEFAULT_TYPE, file_key: str):
    keyboard = [
        [InlineKeyboardButton("🎀 Download 🎀", callback_data=f"getlink_{file_key}")],
        [InlineKeyboardButton("Tutorial", url="https://t.me/your_tutorial_link")],
        [InlineKeyboardButton("Premium", url="https://t.me/your_premium_link")]
    ]
    await context.bot.send_message(chat_id=chat_id, text="Click On Download Button", reply_markup=InlineKeyboardMarkup(keyboard))

# --- मुख्य हैंडलर्स ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id)
    
    if context.args:
        file_key = context.args[0]
        context.user_data['file_key'] = file_key # इसे बटन हैंडलर के लिए याद रखें
        if await is_user_member(user.id, context):
            await send_download_options(user.id, context, file_key)
        else:
            await send_join_request(update, context, file_key)
    else:
        keyboard = [[InlineKeyboardButton("🚀 Go to Main Channel 🚀", url=MAIN_CHANNEL_LINK)]]
        await update.message.reply_text("Welcome! Please use a link from our main channel.", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    data = query.data
    
    await query.answer()

    if data.startswith("check_"):
        file_key = data.split("_", 1)[1]
        if await is_user_member(user.id, context):
            await query.message.delete()
            await send_download_options(user.id, context, file_key)
        else:
            await query.answer("You haven't joined all channels yet. Please try again.", show_alert=True)
    
    elif data.startswith("getlink_"):
        file_key = data.split("_", 1)[1]
        secure_token = generate_secure_token(file_key, user.id)
        if secure_token:
            worker_url = f"https://t.me/{WORKER_BOT_USERNAME}?start={secure_token}"
            text = f"BELOW IS YOUR LINK:\n\n`{worker_url}`"
            await query.message.edit_text(text, parse_mode=ParseMode.MARKDOWN_V2)
        else:
            await query.message.edit_text("Sorry, could not generate a secure link.")

async def id_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ... (ID हैंडलर का पूरा कोड)
async def get_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ... (Get हैंडलर का पूरा कोड)
async def broadcast_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ... (ब्रॉडकास्ट हैंडलर का पूरा कोड)

def setup_handlers(application):
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("id", id_handler))
    application.add_handler(CommandHandler("get", get_handler))
    application.add_handler(CommandHandler("broadcast", broadcast_handler))
    application.add_handler(CallbackQueryHandler(button_handler))
