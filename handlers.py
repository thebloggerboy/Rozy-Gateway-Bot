# rozy-gateway-bot/handlers.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from config import WORKER_BOT_USERNAME, ADMIN_IDS, FORCE_SUB_CHANNELS
from database import generate_secure_token

# --- हेल्पर फंक्शन्स ---
async def is_user_member(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    if user_id in ADMIN_IDS: return True
    for channel in FORCE_SUB_CHANNELS:
        try:
            member = await context.bot.get_chat_member(chat_id=channel["chat_id"], user_id=user_id)
            if member.status not in ['member', 'administrator', 'creator']: return False
        except: return False
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
    # यहाँ आप प्रीव्यू फोटो भी भेज सकते हैं
    # photo_url = "URL_OF_YOUR_PREVIEW_PHOTO"
    # await context.bot.send_photo(chat_id=update_or_query.effective_chat.id, photo=photo_url)
    
    keyboard = [
        [InlineKeyboardButton("🎀 Download 🎀", callback_data=f"getlink_{file_key}")],
        [InlineKeyboardButton("Tutorial", url="https://t.me/your_tutorial_link")],
        [InlineKeyboardButton("Premium", url="https://t.me/your_premium_link")]
    ]
    text = "Click On Download Button"
    if isinstance(update_or_query, Update):
        await update_or_query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    else: # It's a query
        await update_or_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

# --- हैंडलर्स ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not context.args:
        await update.message.reply_text("Welcome! Please use a link from our main channel."); return
    
    file_key = context.args[0]
    context.user_data['file_key'] = file_key

    if await is_user_member(user.id, context):
        await send_download_options(update, context)
    else:
        await send_join_request(update, context)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    await query.answer()

    if query.data.startswith("check_"):
        if await is_user_member(user.id, context):
            await send_download_options(query, context)
        else:
            await query.answer("You haven't joined all channels yet. Please try again.", show_alert=True)
    
    elif query.data.startswith("getlink_"):
        file_key = query.data.split("_", 1)[1]
        secure_token = generate_secure_token(file_key, user.id)
        if secure_token:
            worker_url = f"https://t.me/{WORKER_BOT_USERNAME}?start={secure_token}"
            # यहाँ आप लिंक शॉर्टनर का इस्तेमाल कर सकते हैं
            # short_url = shorten_link(worker_url) # एक फंक्शन जो लिंक को छोटा करे
            text = f"BELOW IS YOUR LINK:\n\n`{worker_url}`"
            await query.message.edit_text(text, parse_mode="MarkdownV2")
        else:
            await query.message.edit_text("Sorry, could not generate a secure link.")

def setup_handlers(application):
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
