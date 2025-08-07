from supabase import create_client, Client
import os

# Ganti dengan URL dan Anon Key dari Supabase kamu
SUPABASE_URL = https://supabase.com/dashboard/project/nwsjgtrzyrebdaioczhj
SUPABASE_KEY = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im53c2pndHJ6eXJlYmRhaW9jemhqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ1NjM4ODgsImV4cCI6MjA3MDEzOTg4OH0.jxmfTFHp7vSwkzE5dVgw7-WKdgKUTxIsysaeA9DRSCw

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def insert_journal(data: dict):
    response = supabase.table("trading_journal").insert(data).execute()
    return response

def fetch_all_journals():
    response = supabase.table("trading_journal").select("*").order("tanggal", desc=True).execute()
    return response.data
