# rozy-gateway-bot/handlers.py (Final and Corrected)

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from telegram.error import BadRequest
import logging

# config और database से ज़रूरी चीजें इम्पोर्ट करें
from config import WORKER_BOT_USERNAME, ADMIN_IDS, FORCE_SUB_CHANNELS, MAIN_CHANNEL_LINK
from database import generate_secure_token

logger = logging.getLogger(__name__)

# --- हेल्पर फंक्शन्स ---
async def is_user_member(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    if user_id in ADMIN_IDS: return True
    if not FORCE_SUB_CHANNELS: return True
    for channel in FORCE_SUB_CHANNELS:
        try:
            member = await context.bot.get_chat_member(chat_id=channel["chat_id"], user_id=user_id)
            if member.status not in ['member', 'administrator', 'creator']: return False
        except BadRequest:
            logger.warning(f"Failed to check membership for user {user_id} in chat {channel['chat_id']}. Is bot an admin?")
            return False
    return True

async def send_join_request(update_or_query, context: ContextTypes.DEFAULT_TYPE):
    file_key = context.user_data.get('file_key')
    if not file_key: return
    
    join_buttons = [InlineKeyboardButton(ch["name"], url=ch["invite_link"]) for ch in FORCE_SUB_CHANNELS]
    keyboard = [join_buttons, [InlineKeyboardButton("✅ Joined", callback_data=f"check_{file_key}")]]
    text = "Please join our channels first to get the download link."

    if isinstance(update_or_query, Update):
        await update_or_query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    else: # It's a query
        await update_or_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def send_download_options(update_or_query, context: ContextTypes.DEFAULT_TYPE):
    file_key = context.user_data.get('file_key')
    
    keyboard = [
        [InlineKeyboardButton("🎀 Download 🎀", callback_data=f"getlink_{file_key}")],
        [InlineKeyboardButton("Tutorial", url="https://t.me/your_tutorial_link")], # <-- अपनी लिंक डालें
        [InlineKeyboardButton("Premium", url="https://t.me/your_premium_link")]  # <-- अपनी लिंक डालें
    ]
    text = "Click On Download Button"

    if isinstance(update_or_query, Update):
        await update_or_query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    else: # It's a query
        await update_or_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

# --- मुख्य हैंडलर्स ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    if context.args:
        file_key = context.args[0]
        context.user_data['file_key'] = file_key

        if await is_user_member(user.id, context):
            await send_download_options(update, context)
        else:
            await send_join_request(update, context)
    else:
        # --- यहाँ मेन चैनल का बटन जोड़ा गया है ---
        keyboard = [[InlineKeyboardButton("🚀 Go to Main Channel 🚀", url=MAIN_CHANNEL_LINK)]]
        await update.message.reply_text(
            "Welcome! Please use a link from our main channel to get files.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    data = query.data

    if data.startswith("check_"):
        await query.answer() # पहले क्लिक का जवाब दें
        if await is_user_member(user.id, context):
            await send_download_options(query, context)
        else:
            await query.answer("You haven't joined all channels yet. Please try again.", show_alert=True)
    
    elif data.startswith("getlink_"):
        await query.answer()
        file_key = data.split("_", 1)[1]
        secure_token = generate_secure_token(file_key, user.id)
        if secure_token:
            worker_url = f"https://t.me/{WORKER_BOT_USERNAME}?start={secure_token}"
            text = f"BELOW IS YOUR LINK:\n\n`{worker_url}`"
            await query.message.edit_text(text, parse_mode="MarkdownV2")
        else:
            await query.message.edit_text("Sorry, could not generate a secure link.")

def setup_handlers(application):
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
