# supabase_client.py
from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()  # Load .env file jika kamu menyimpan API key di sana

SUPABASE_URL = os.getenv"https://nwsjgtrzyrebdaioczhj.supabase.co"
SUPABASE_KEY = os.getenv"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im53c2pndHJ6eXJlYmRhaW9jemhqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ1NjM4ODgsImV4cCI6MjA3MDEzOTg4OH0.jxmfTFHp7vSwkzE5dVgw7-WKdgKUTxIsysaeA9DRSCw"

def get_supabase_client() -> Client:
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise Exception("Supabase URL atau KEY belum diatur di environment variables.")
    
    return create_client(SUPABASE_URL, SUPABASE_KEY)
