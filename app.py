import streamlit as st
from supabase import create_client, Client
from datetime import datetime
import pandas as pd
import uuid

# ========== Konfigurasi Supabase ==========
SUPABASE_URL = "https://nwsjgtrzyrebdaioczhj.supabase.co"  
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im53c2pndHJ6eXJlYmRhaW9jemhqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ1NjM4ODgsImV4cCI6MjA3MDEzOTg4OH0.jxmfTFHp7vSwkzE5dVgw7-WKdgKUTxIsysaeA9DRSCw"  
TABLE_NAME = "keuangan"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ========== Fungsi CRUD ==========

def insert_transaksi(data):
    return supabase.table(TABLE_NAME).insert(data).execute()

def fetch_all_transaksi():
    response = supabase.table(TABLE_NAME).select("*").order("tanggal", desc=True).execute()
    return response.data if response.data else []

def delete_transaksi(row_id):
    return supabase.table(TABLE_NAME).delete().eq("id", row_id).execute()

# ========== Form Input ==========
def render_form():
    st.header("📥 Tambah Transaksi")
    with st.form("form_transaksi"):
        tanggal = st.date_input("Tanggal")
        kategori = st.selectbox("Kategori", ["Pemasukan", "Pengeluaran"])
        jenis = st.text_input("Jenis Transaksi (misal: Gaji, Makan, dll)")
        metode = st.selectbox("Metode Pembayaran", ["Cash", "E-Wallet", "Bank Transfer"])
        jumlah = st.number_input("Jumlah", min_value=0.0, step=1000.0, format="%.2f")
        keterangan = st.text_area("Keterangan")

        submitted = st.form_submit_button("Simpan")
        if submitted:
            data = {
                "id": str(uuid.uuid4()),
                "tanggal": str(tanggal),
                "kategori": kategori,
                "jenis": jenis,
                "metode": metode,
                "jumlah": jumlah,
                "keterangan": keterangan,
                "created_at": datetime.now().isoformat()
            }
            insert_transaksi(data)
            st.success("Transaksi berhasil disimpan!")

# ========== Tabel Transaksi ==========
def render_transaction_table(df):
    st.header("📊 Daftar Transaksi")

    if df.empty:
        st.info("Belum ada transaksi.")
        return

    df_view = df.copy()
    df_view["tanggal"] = pd.to_datetime(df_view["tanggal"]).dt.strftime("%d-%m-%Y")
    st.dataframe(df_view.drop(columns=["id", "created_at"]))

    selected_id = st.selectbox("Pilih ID transaksi untuk dihapus", df["id"])
    if st.button("🗑️ Hapus Transaksi"):
        delete_transaksi(selected_id)
        st.success("Transaksi berhasil dihapus!")
        st.experimental_rerun()

# ========== Analisis Sederhana ==========
def render_summary(df):
    st.header("📈 Ringkasan Keuangan")

    pemasukan = df[df["kategori"] == "Pemasukan"]["jumlah"].sum()
    pengeluaran = df[df["kategori"] == "Pengeluaran"]["jumlah"].sum()
    saldo = pemasukan - pengeluaran

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Pemasukan", f"Rp {pemasukan:,.2f}")
    col2.metric("Total Pengeluaran", f"Rp {pengeluaran:,.2f}")
    col3.metric("Saldo Akhir", f"Rp {saldo:,.2f}")

# ========== Main App ==========
def main():
    st.set_page_config(page_title="Finance Tracker", page_icon="💸", layout="wide")
    st.title("💸 Aplikasi Keuangan Pribadi")
    
    df = pd.DataFrame(fetch_all_transaksi())
    
    tab1, tab2, tab3 = st.tabs(["➕ Tambah", "📋 Daftar", "📊 Ringkasan"])
    
    with tab1:
        render_form()
    with tab2:
        render_transaction_table(df)
    with tab3:
        render_summary(df)

if __name__ == "__main__":
    main()
