import os
import logging
import asyncio
import json
import random
import string
from threading import Thread
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
from telegram.constants import ParseMode
from telegram.error import BadRequest
from supabase import create_client, Client
from dotenv import load_dotenv

# --- सेटअप ---
load_dotenv()
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# --- एनवायरनमेंट वेरिएबल्स से सीक्रेट्स और कॉन्फ़िगरेशन लें ---
TOKEN = os.environ.get("GATEWAY_BOT_TOKEN")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
ADMIN_IDS = [int(i) for i in os.environ.get("ADMIN_IDS", "6056915535").split(',')]
WORKER_BOT_USERNAME = os.environ.get("WORKER_BOT_USERNAME", "YourRubyBotUsername")
MAIN_CHANNEL_LINK = os.environ.get("MAIN_CHANNEL_LINK", "https://t.me/YourMainChannel")
try:
    FORCE_SUB_CHANNELS = json.loads(os.environ.get("FORCE_SUB_CHANNELS", "[]"))
except:
    FORCE_SUB_CHANNELS = []

# --- Supabase क्लाइंट और डेटाबेस फाइल ---
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
DB_FILE = 'rozy_users.json'

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f:
            try: return json.load(f)
            except json.JSONDecodeError: return {"users": []}
    return {"users": []}
def save_db(data):
    with open(DB_FILE, 'w') as f: json.dump(data, f, indent=4)
db = load_db()
def add_user(user_id):
    if user_id not in db["users"]: db["users"].append(user_id); save_db(db)

def generate_secure_token(file_key, user_id):
    try:
        token = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
        supabase.table('secure_links').insert({"token": token, "file_key": file_key, "user_id": user_id}).execute()
        return token
    except Exception as e:
        logger.error(f"Error generating token: {e}"); return None

# --- Keep-Alive सर्वर ---
app = Flask('')
@app.route('/')
def home(): return "Rozy Gateway Bot is alive!"
def run_flask(): app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
def keep_alive(): Thread(target=run_flask).start()

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
    await update.message.reply_text("Please join our channels first.", reply_markup=InlineKeyboardMarkup(keyboard))

# main.py के अंदर
async def send_download_options(chat_id: int, context: ContextTypes.DEFAULT_TYPE, file_key: str):
    # --- यहाँ मुख्य बदलाव है ---
    # अब हम file_key को सीधे getlink बटन के callback_data में डाल रहे हैं
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
        if await is_user_member(user.id, context): await send_download_options(user.id, context, file_key)
        else: await send_join_request(update, context, file_key)
    else:
        keyboard = [[InlineKeyboardButton("🚀 Go to Main Channel 🚀", url=MAIN_CHANNEL_LINK)]]
        await update.message.reply_text("Welcome! Please use a link from our main channel.", reply_markup=InlineKeyboardMarkup(keyboard))

# main.py के अंदर
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query, user, data = update.callback_query, query.from_user, query.data
    
    # --- चेक बटन का लॉजिक ---
    if data.startswith("check_"):
        await query.answer()
        file_key = data.split("_", 1)[1] # हम key को सीधे data से ले रहे हैं
        if await is_user_member(user.id, context):
            await query.message.delete()
            await send_download_options(user.id, context, file_key)
        else:
            await query.answer("You haven't joined all channels yet.", show_alert=True)
            
    # --- गेट लिंक बटन का लॉजिक ---
    elif data.startswith("getlink_"):
        await query.answer()
        file_key = data.split("_", 1)[1] # हम key को सीधे data से ले रहे हैं
        token = generate_secure_token(file_key, user.id)
        if token:
            url = f"https://t.me/{WORKER_BOT_USERNAME}?start={token}"
            await query.message.edit_text(f"BELOW IS YOUR LINK:\n\n`{url}`", parse_mode="MarkdownV2")
        else:
            await query.message.edit_text("Sorry, could not generate link.")
# --- मुख्य फंक्शन ---
def main():
    if not all([TOKEN, SUPABASE_URL, SUPABASE_KEY]): logger.critical("Missing env variables!"); return
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    keep_alive()
    logger.info("Rozy Gateway Bot is polling!")
    application.run_polling()

if __name__ == '__main__':
    main()
