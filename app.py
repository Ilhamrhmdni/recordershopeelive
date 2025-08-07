# File: finance_tracker.py

import streamlit as st
from supabase import create_client
from datetime import datetime
import pandas as pd
import os
from dotenv import load_dotenv

# --- LOAD ENVIRONMENT ---
load_dotenv()

# --- KONFIGURASI SUPABASE ---
SUPABASE_URL = os.getenv"https://nwsjgtrzyrebdaioczhj.supabase.co"
SUPABASE_KEY = os.getenv"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im53c2pndHJ6eXJlYmRhaW9jemhqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ1NjM4ODgsImV4cCI6MjA3MDEzOTg4OH0.jxmfTFHp7vSwkzE5dVgw7-WKdgKUTxIsysaeA9DRSCw"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
TABLE_NAME = "keuangan"

# --- FUNGSI CRUD ---
def insert_transaksi(data: dict):
    return supabase.table(TABLE_NAME).insert(data).execute()

def get_all_transaksi():
    return supabase.table(TABLE_NAME).select("*").order("tanggal", desc=False).execute().data

def delete_transaksi(row_id: int):
    return supabase.table(TABLE_NAME).delete().eq("id", row_id).execute()

def update_transaksi(row_id: int, updated_data: dict):
    return supabase.table(TABLE_NAME).update(updated_data).eq("id", row_id).execute()

# --- FORM TAMBAH TRANSAKSI ---
def render_form():
    with st.form("form_transaksi"):
        tanggal = st.date_input("Tanggal", value=datetime.today())
        kategori = st.selectbox("Kategori", ["Pemasukan", "Pengeluaran"])
        deskripsi = st.text_input("Deskripsi")
        jumlah = st.number_input("Jumlah", min_value=0.0, format="%.2f")
        metode = st.selectbox("Metode Pembayaran", ["Cash", "Transfer", "E-Wallet"])
        submitted = st.form_submit_button("Simpan")

        if submitted:
            if not deskripsi:
                st.warning("Deskripsi tidak boleh kosong!")
                return None
            if jumlah == 0:
                st.warning("Jumlah tidak boleh 0!")
                return None
            return {
                "tanggal": tanggal.isoformat(),
                "kategori": kategori,
                "deskripsi": deskripsi,
                "jumlah": jumlah,
                "metode": metode
            }
    return None

# --- FORM EDIT TRANSAKSI ---
def render_edit_form(data, row_id):
    with st.form(f"edit_form_{row_id}"):
        tanggal = st.date_input("Tanggal", value=pd.to_datetime(data['tanggal']))
        kategori = st.selectbox("Kategori", ["Pemasukan", "Pengeluaran"], index=["Pemasukan", "Pengeluaran"].index(data['kategori']))
        deskripsi = st.text_input("Deskripsi", value=data['deskripsi'])
        jumlah = st.number_input("Jumlah", value=float(data['jumlah']), min_value=0.0, format="%.2f")
        metode = st.selectbox("Metode Pembayaran", ["Cash", "Transfer", "E-Wallet"], index=["Cash", "Transfer", "E-Wallet"].index(data['metode']))
        submit = st.form_submit_button("Simpan Perubahan")

        if submit:
            updated_data = {
                "tanggal": tanggal.isoformat(),
                "kategori": kategori,
                "deskripsi": deskripsi,
                "jumlah": jumlah,
                "metode": metode
            }
            update_transaksi(row_id, updated_data)
            st.success("Transaksi berhasil diubah.")

# --- TABEL TRANSAKSI DENGAN FILTER ---
def render_transaction_table(df):
    with st.expander("🔍 Filter"):
        kategori_filter = st.multiselect("Kategori", df["kategori"].unique(), default=df["kategori"].unique())
        metode_filter = st.multiselect("Metode", df["metode"].unique(), default=df["metode"].unique())
        df = df[df["kategori"].isin(kategori_filter) & df["metode"].isin(metode_filter)]

    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Unduh Data CSV", csv, "data_keuangan.csv", "text/csv")

    with st.expander("✏️ Edit / 🗑️ Hapus Transaksi"):
        selected_id = st.number_input("ID Transaksi", min_value=1, step=1)
        action = st.radio("Aksi", ["Edit", "Hapus"], horizontal=True)
        if st.button("Proses"):
            selected_row = df[df['id'] == selected_id]
            if selected_row.empty:
                st.error("ID tidak ditemukan.")
            elif action == "Hapus":
                delete_transaksi(int(selected_id))
                st.success("Transaksi berhasil dihapus.")
            else:
                render_edit_form(selected_row.iloc[0], selected_id)

# --- ANALISIS KEUANGAN ---
def render_financial_analysis(df):
    total_pemasukan = df[df['kategori'] == 'Pemasukan']['jumlah'].sum()
    total_pengeluaran = df[df['kategori'] == 'Pengeluaran']['jumlah'].sum()
    saldo_akhir = total_pemasukan - total_pengeluaran

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Pemasukan", f"Rp {total_pemasukan:,.2f}")
    col2.metric("Total Pengeluaran", f"Rp {total_pengeluaran:,.2f}")
    col3.metric("Saldo Akhir", f"Rp {saldo_akhir:,.2f}")

    st.subheader("📊 Grafik Kategori")
    chart_data = df.groupby("kategori")["jumlah"].sum().reset_index()
    st.bar_chart(chart_data, x="kategori", y="jumlah")

    st.subheader("📈 Grafik Tren Bulanan")
    df['tanggal'] = pd.to_datetime(df['tanggal'])
    df['bulan'] = df['tanggal'].dt.to_period("M").astype(str)
    trend_data = df.groupby('bulan')['jumlah'].sum().reset_index()
    st.line_chart(trend_data, x='bulan', y='jumlah')

# --- KALENDER TRANSAKSI ---
def render_calendar_view(df):
    df['tanggal'] = pd.to_datetime(df['tanggal'])
    df['tanggal_str'] = df['tanggal'].dt.strftime('%Y-%m-%d')
    df_grouped = df.groupby("tanggal_str").agg({
        "jumlah": "sum",
        "kategori": lambda x: ', '.join(set(x))
    }).reset_index()
    st.dataframe(df_grouped, use_container_width=True)

# --- KONFIGURASI LAYOUT ---
st.set_page_config(page_title="Finance Tracker", layout="wide")
st.title("💰 Finance Tracker App")

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("## 💼 Finance Tracker")
    st.markdown("Versi 1.1.0")
    st.markdown("---")
    menu = st.radio("📌 Navigasi", [
        "📥 Form Input", 
        "📋 Tabel Transaksi", 
        "📊 Analisis Keuangan", 
        "🗓️ Kalender Transaksi"
    ])
    st.markdown("---")
    st.markdown("Built by Ilham ❤️", unsafe_allow_html=True)

# --- RENDER HALAMAN SESUAI MENU ---
if menu == "📥 Form Input":
    st.subheader("📝 Tambah Transaksi")
    data = render_form()
    if data:
        insert_transaksi(data)
        st.success("Transaksi berhasil disimpan!")

elif menu == "📋 Tabel Transaksi":
    st.subheader("📋 Riwayat Transaksi")
    df = pd.DataFrame(get_all_transaksi())
    if df.empty:
        st.info("Belum ada data transaksi.")
    else:
        render_transaction_table(df)

elif menu == "📊 Analisis Keuangan":
    st.subheader("📊 Analisis Keuangan")
    df = pd.DataFrame(get_all_transaksi())
    if df.empty:
        st.info("Belum ada data untuk dianalisis.")
    else:
        render_financial_analysis(df)

elif menu == "🗓️ Kalender Transaksi":
    st.subheader("📅 Kalender Transaksi")
    df = pd.DataFrame(get_all_transaksi())
    if df.empty:
        st.info("Belum ada data transaksi.")
    else:
        render_calendar_view(df)
