import os, json, random, string
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

DB_FILE = 'rozy_users.json' # Rozy के यूज़र्स के लिए अलग फाइल

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
    if user_id not in db["users"]:
        db["users"].append(user_id); save_db(db)

def get_all_user_ids():
    return db["users"]

def generate_secure_token(file_key, user_id):
    try:
        token = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
        supabase.table('secure_links').insert({"token": token, "file_key": file_key, "user_id": user_id}).execute()
        return token
    except Exception as e:
        print(f"Error generating token: {e}"); return None
