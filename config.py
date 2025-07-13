# rozy-gateway-bot/config.py
import os

# --- टोकन को एनवायरनमेंट से लें ---
TOKEN = os.environ.get("GATEWAY_BOT_TOKEN")

# 1. आपकी एडमिन ID
ADMIN_IDS = [6056915535] 

# 2. वर्कर बॉट का यूजरनेम
WORKER_BOT_USERNAME = "RubyWorkerBot" # <-- यहाँ Ruby बॉट का सही यूजरनेम डालें

# 3. मेन चैनल का लिंक
MAIN_CHANNEL_LINK = "https://t.me/Primium_Links" # <-- यहाँ अपने मेन चैनल का लिंक डालें

# 4. फोर्स सब्सक्राइब के लिए चैनल
FORCE_SUB_CHANNELS = [
    {"chat_id": -1002599545967, "name": "Join 1", "invite_link": "https://t.me/+p2ErvvDmitZmYzdl"},
    {"chat_id": -1002391821078, "name": "Join 2", "invite_link": "https://t.me/+T4LO1ePja_I5NWQ1"}
]
