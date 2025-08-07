import streamlit as st
from supabase import create_client
from datetime import datetime
import pandas as pd

# --- KONFIGURASI SUPABASE ---
SUPABASE_URL = "https://nwsjgtrzyrebdaioczhj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im53c2pndHJ6eXJlYmRhaW9jemhqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ1NjM4ODgsImV4cCI6MjA3MDEzOTg4OH0.jxmfTFHp7vSwkzE5dVgw7-WKdgKUTxIsysaeA9DRSCw"
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

# --- UI Form Input ---
def render_form():
    with st.form("form_transaksi"):
        tanggal = st.date_input("Tanggal", value=datetime.today())
        kategori = st.selectbox("Kategori", ["Pemasukan", "Pengeluaran"])
        deskripsi = st.text_input("Deskripsi")
        jumlah = st.number_input("Jumlah", min_value=0.0, format="%.2f")
        metode = st.selectbox("Metode Pembayaran", ["Cash", "Transfer", "E-Wallet"])
        submitted = st.form_submit_button("Simpan")

        if submitted:
            return {
                "tanggal": tanggal.isoformat(),
                "kategori": kategori,
                "deskripsi": deskripsi,
                "jumlah": jumlah,
                "metode": metode
            }
    return None

# --- Tabel Transaksi ---
def render_transaction_table(df):
    st.dataframe(df, use_container_width=True)
    with st.expander("🗑️ Hapus Transaksi"):
        selected_id = st.number_input("ID Transaksi yang ingin dihapus", min_value=1, step=1)
        if st.button("Hapus"):
            delete_transaksi(int(selected_id))
            st.success("Transaksi berhasil dihapus.")

# --- Analisis Keuangan ---
def render_financial_analysis(df):
    total_pemasukan = df[df['kategori'] == 'Pemasukan']['jumlah'].sum()
    total_pengeluaran = df[df['kategori'] == 'Pengeluaran']['jumlah'].sum()
    saldo_akhir = total_pemasukan - total_pengeluaran

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Pemasukan", f"Rp {total_pemasukan:,.2f}")
    col2.metric("Total Pengeluaran", f"Rp {total_pengeluaran:,.2f}")
    col3.metric("Saldo Akhir", f"Rp {saldo_akhir:,.2f}")

    st.subheader("📊 Grafik Berdasarkan Kategori")
    kategori_chart = df.groupby("kategori")["jumlah"].sum().reset_index()
    st.bar_chart(kategori_chart, x="kategori", y="jumlah")

    st.subheader("📌 Grafik Berdasarkan Deskripsi")
    deskripsi_chart = df.groupby("deskripsi")["jumlah"].sum().reset_index().sort_values(by="jumlah", ascending=False)
    st.bar_chart(deskripsi_chart, x="deskripsi", y="jumlah")

# --- Kalender Transaksi ---
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
st.title("💰 Finance Tracker")

# --- SIDEBAR RAPIH ---
with st.sidebar:
    st.title("📘 Finance Menu")
    menu = st.radio("📂 Navigasi", [
        "Home",
        "Tambah Transaksi",
        "Tabel Transaksi",
        "Analisis Keuangan",
        "Kalender Transaksi"
    ])
    st.markdown("---")
    st.caption("🔧 Dibuat oleh Ilham")

# --- RENDER KONTEN BERDASARKAN MENU ---
if menu == "🏠 Home":
    st.image("https://i.imgur.com/BXzG7j1.png", width=400)
    st.subheader("Selamat Datang di Aplikasi Finance Tracker 👋")
    st.write("""
    Aplikasi ini membantu kamu mencatat, memantau, dan menganalisis keuangan pribadi secara sederhana.
    Mulai dari pemasukan, pengeluaran, grafik keuangan, hingga laporan per tanggal.
    """)

elif menu == "➕ Tambah Transaksi":
    st.subheader("📝 Tambah Transaksi")
    data = render_form()
    if data:
        insert_transaksi(data)
        st.success("✅ Transaksi berhasil disimpan!")

elif menu == "📄 Tabel Transaksi":
    st.subheader("📋 Riwayat Transaksi")
    df = pd.DataFrame(get_all_transaksi())
    if df.empty:
        st.info("Belum ada data transaksi.")
    else:
        render_transaction_table(df)

elif menu == "📊 Analisis Keuangan":
    st.subheader("📈 Analisis Keuangan")
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
