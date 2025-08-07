# data_handler.py
from supabase_client import get_supabase_client

supabase = get_supabase_client()

TABLE_NAME = "transaksi"

def insert_transaksi(data: dict):
    """Insert data transaksi ke tabel Supabase."""
    response = supabase.table(TABLE_NAME).insert(data).execute()
    return response

def get_all_transaksi():
    """Ambil semua data transaksi."""
    response = supabase.table(TABLE_NAME).select("*").order("tanggal", desc=False).execute()
    return response.data

def delete_transaksi(row_id: int):
    """Hapus data berdasarkan ID."""
    response = supabase.table(TABLE_NAME).delete().eq("id", row_id).execute()
    return response

def update_transaksi(row_id: int, updated_data: dict):
    """Update data berdasarkan ID."""
    response = supabase.table(TABLE_NAME).update(updated_data).eq("id", row_id).execute()
    return response

def filter_transaksi(kategori=None, metode=None, tanggal_awal=None, tanggal_akhir=None):
    """Ambil data transaksi dengan filter opsional."""
    query = supabase.table(TABLE_NAME).select("*")

    if kategori:
        query = query.eq("kategori", kategori)
    if metode:
        query = query.eq("metode", metode)
    if tanggal_awal and tanggal_akhir:
        query = query.gte("tanggal", tanggal_awal).lte("tanggal", tanggal_akhir)

    response = query.order("tanggal", desc=False).execute()
    return response.data
