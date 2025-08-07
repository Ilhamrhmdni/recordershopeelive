from supabase import create_client, Client
import os

# Ganti dengan URL dan Anon Key dari Supabase kamu
SUPABASE_URL = "https://xyzcompany.supabase.co"
SUPABASE_KEY = "your-anon-key"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def insert_journal(data: dict):
    response = supabase.table("trading_journal").insert(data).execute()
    return response

def fetch_all_journals():
    response = supabase.table("trading_journal").select("*").order("tanggal", desc=True).execute()
    return response.data
