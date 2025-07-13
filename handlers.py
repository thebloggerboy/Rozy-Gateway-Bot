import logging, asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from config import WORKER_BOT_USERNAME, ADMIN_IDS, FORCE_SUB_CHANNELS, MAIN_CHANNEL_LINK
from database import generate_secure_token, add_user, get_all_user_ids, db, save_db

logger = logging.getLogger(__name__)

# --- हेल्पर फंक्शन्स ---
async def is_user_member(user_id, context):
    # ... (यह फंक्शन वैसा ही रहेगा)
async def send_join_request(update, context, file_key):
    # ... (यह फंक्शन वैसा ही रहेगा)
async def send_download_options(chat_id, context, file_key):
    # ... (यह फंक्शन वैसा ही रहेगा)

# --- मुख्य हैंडलर्स ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id) # नए यूजर को डेटाबेस में जोड़ें
    
    if context.args:
        file_key = context.args[0]
        if await is_user_member(user.id, context): await send_download_options(user.id, context, file_key)
        else: await send_join_request(update, context, file_key)
    else:
        keyboard = [[InlineKeyboardButton("🚀 Go to Main Channel 🚀", url=MAIN_CHANNEL_LINK)]]
        await update.message.reply_text("Welcome! Please use a link from our main channel.", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ... (यह फंक्शन वैसा ही रहेगा)

# --- एडमिन कमांड्स ---
async def broadcast_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS: return
    msg = update.message.reply_to_message
    if not msg: await update.message.reply_text("Please reply to a message to broadcast."); return
    
    users = get_all_user_ids(); sent, failed = 0, 0
    await update.message.reply_text(f"Broadcasting to {len(users)} users...")
    
    for user_id in users:
        try:
            await msg.copy(chat_id=int(user_id), reply_markup=msg.reply_markup)
            sent += 1; await asyncio.sleep(0.1)
        except Exception as e:
            failed += 1; logger.error(f"Broadcast failed for {user_id}: {e}")
            if "bot was blocked" in str(e): db["users"].pop(str(user_id), None)
    save_db(db)
    await update.message.reply_text(f"Broadcast finished!\nSent: {sent}, Failed: {failed}")

def setup_handlers(application):
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("broadcast", broadcast_handler))
    application.add_handler(CallbackQueryHandler(button_handler))
