# rozy-gateway-bot/handlers.py (Final with Corrected Button Handler)

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from telegram.error import BadRequest

# config और database से ज़रूरी चीजें इम्पोर्ट करें
from config import WORKER_BOT_USERNAME, ADMIN_IDS, FORCE_SUB_CHANNELS, MAIN_CHANNEL_LINK
from database import generate_secure_token, add_user

logger = logging.getLogger(__name__)

# --- हेल्पर फंक्शन्स ---
async def is_user_member(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    if user_id in ADMIN_IDS: return True
    for channel in FORCE_SUB_CHANNELS:
        try:
            member = await context.bot.get_chat_member(chat_id=channel["chat_id"], user_id=user_id)
            if member.status not in ['member', 'administrator', 'creator']: return False
        except BadRequest:
            logger.warning(f"Failed to check membership for user {user_id}. Is bot an admin in chat {channel['chat_id']}?")
            return False
    return True

async def send_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file_key = context.user_data.get('file_key')
    if not file_key: return
    join_buttons = [InlineKeyboardButton(ch["name"], url=ch["invite_link"]) for ch in FORCE_SUB_CHANNELS]
    keyboard = [join_buttons, [InlineKeyboardButton("✅ Joined", callback_data=f"check_{file_key}")]]
    await update.message.reply_text("Please join our channels first.", reply_markup=InlineKeyboardMarkup(keyboard))

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
        context.user_data['file_key'] = file_key
        if await is_user_member(user.id, context):
            await send_download_options(user.id, context, file_key)
        else:
            await send_join_request(update, context)
    else:
        keyboard = [[InlineKeyboardButton("🚀 Go to Main Channel 🚀", url=MAIN_CHANNEL_LINK)]]
        await update.message.reply_text("Welcome! Please use a link from our main channel.", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    data = query.data
    
    # --- चेक बटन का लॉजिक ---
    if data.startswith("check_"):
        file_key = context.user_data.get('file_key')
        if not file_key:
            await query.answer("Something went wrong, please try the main link again.", show_alert=True)
            return

        # पहले मेंबरशिप चेक करें
        if await is_user_member(user.id, context):
            # अगर मेंबर है, तो सामान्य जवाब दें और काम करें
            await query.answer()
            await query.message.delete()
            await send_download_options(user.id, context, file_key)
        else:
            # अगर मेंबर नहीं है, तो सिर्फ पॉप-अप अलर्ट वाला जवाब दें
            await query.answer("You haven't joined all channels yet. Please try again.", show_alert=True)
            
    # --- गेट लिंक बटन का लॉजिक ---
    elif data.startswith("getlink_"):
        await query.answer()
        file_key = data.split("_", 1)[1]
        token = generate_secure_token(file_key, user.id)
        if token:
            url = f"https://t.me/{WORKER_BOT_USERNAME}?start={token}"
            await query.message.edit_text(f"BELOW IS YOUR LINK:\n\n`{url}`", parse_mode="MarkdownV2")
        else:
            await query.message.edit_text("Sorry, could not generate link.")
    
    # --- अगर कोई और बटन है तो ---
    else:
        # एक खाली जवाब भेजें ताकि लोडिंग बंद हो जाए
        await query.answer()

def setup_handlers(application):
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
