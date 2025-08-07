# supabase_client.py
from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()  # Load .env file jika kamu menyimpan API key di sana

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def get_supabase_client() -> Client:
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise Exception("Supabase URL atau KEY belum diatur di environment variables.")
    
    return create_client(SUPABASE_URL, SUPABASE_KEY)
