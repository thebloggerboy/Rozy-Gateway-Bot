# rozy-gateway-bot/handlers.py
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from telegram.error import BadRequest
from config import WORKER_BOT_USERNAME, ADMIN_IDS, FORCE_SUB_CHANNELS, MAIN_CHANNEL_LINK
from database import generate_secure_token, add_user

logger = logging.getLogger(__name__)

async def is_user_member(user_id, context):
    if user_id in ADMIN_IDS: return True
    for channel in FORCE_SUB_CHANNELS:
        try:
            member = await context.bot.get_chat_member(chat_id=channel["chat_id"], user_id=user_id)
            if member.status not in ['member', 'administrator', 'creator']: return False
        except BadRequest: return False
    return True

async def send_join_request(update, context, file_key):
    join_buttons = [InlineKeyboardButton(ch["name"], url=ch["invite_link"]) for ch in FORCE_SUB_CHANNELS]
    keyboard = [join_buttons, [InlineKeyboardButton("✅ Joined", callback_data=f"check_{file_key}")]]
    await update.message.reply_text("Please join our channels first.", reply_markup=InlineKeyboardMarkup(keyboard))

async def send_download_options(chat_id, context, file_key):
    keyboard = [
        [InlineKeyboardButton("🎀 Download 🎀", callback_data=f"getlink_{file_key}")],
        [InlineKeyboardButton("Tutorial", url="https://t.me/your_tutorial_link")],
        [InlineKeyboardButton("Premium", url="https://t.me/your_premium_link")]
    ]
    await context.bot.send_message(chat_id=chat_id, text="Click On Download Button", reply_markup=InlineKeyboardMarkup(keyboard))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id)
    if context.args:
        file_key = context.args[0]
        context.user_data['file_key'] = file_key
        if await is_user_member(user.id, context): await send_download_options(user.id, context, file_key)
        else: await send_join_request(update, context, file_key)
    else:
        keyboard = [[InlineKeyboardButton("🚀 Go to Main Channel 🚀", url=MAIN_CHANNEL_LINK)]]
        await update.message.reply_text("Welcome! Please use a link from our main channel.", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query, user, data = update.callback_query, query.from_user, query.data
    await query.answer()
    if data.startswith("check_"):
        file_key = context.user_data.get('file_key')
        if not file_key: await query.answer("Something went wrong, try the main link again.", show_alert=True); return
        if await is_user_member(user.id, context):
            await query.message.delete(); await send_download_options(user.id, context, file_key)
        else: await query.answer("You haven't joined all channels yet.", show_alert=True)
    elif data.startswith("getlink_"):
        file_key = data.split("_", 1)[1]
        token = generate_secure_token(file_key, user.id)
        if token:
            url = f"https://t.me/{WORKER_BOT_USERNAME}?start={token}"
            await query.message.edit_text(f"BELOW IS YOUR LINK:\n\n`{url}`", parse_mode="MarkdownV2")
        else: await query.message.edit_text("Sorry, could not generate link.")

def setup_handlers(application):
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
