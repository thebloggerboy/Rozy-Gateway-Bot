import os
from supabase import create_client, Client
import random, string
from dotenv import load_dotenv

load_dotenv()
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def generate_secure_token(file_key: str, user_id: int):
    try:
        token = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
        supabase.table('secure_links').insert({
            "token": token,
            "file_key": file_key,
            "user_id": user_id
        }).execute()
        return token
    except Exception as e:
        print(f"Error generating token: {e}")
        return None