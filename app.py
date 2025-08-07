import streamlit as st
from supabase import create_client
from datetime import datetime
import pandas as pd

# === KONFIGURASI SUPABASE ===
SUPABASE_URL = "https://nwsjgtrzyrebdaioczhj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im53c2pndHJ6eXJlYmRhaW9jemhqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ1NjM4ODgsImV4cCI6MjA3MDEzOTg4OH0.jxmfTFHp7vSwkzE5dVgw7-WKdgKUTxIsysaeA9DRSCw"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
TABLE_NAME = "keuangan"

# === FUNGSI CRUD ===
def insert_transaksi(data: dict):
    return supabase.table(TABLE_NAME).insert(data).execute()

def get_all_transaksi():
    return supabase.table(TABLE_NAME).select("*").order("tanggal", desc=False).execute().data

def delete_transaksi(row_id: int):
    return supabase.table(TABLE_NAME).delete().eq("id", row_id).execute()

# === FORM INPUT ===
def render_form():
    with st.form("form_transaksi"):
        st.markdown("### ➕ Tambah Transaksi Baru")
        tanggal = st.date_input("🗓️ Tanggal", value=datetime.today())
        kategori = st.selectbox("📂 Kategori", ["Pemasukan", "Pengeluaran"])
        deskripsi = st.text_input("📝 Deskripsi")
        jumlah = st.number_input("💸 Jumlah (Rp)", min_value=0.0, format="%.2f")
        metode = st.selectbox("🏦 Metode Pembayaran", ["Cash", "Transfer", "E-Wallet"])
        submitted = st.form_submit_button("💾 Simpan")

        if submitted:
            return {
                "tanggal": tanggal.isoformat(),
                "kategori": kategori,
                "deskripsi": deskripsi,
                "jumlah": jumlah,
                "metode": metode
            }
    return None

# === TABEL TRANSAKSI ===
def render_transaction_table(df):
    st.markdown("### 📋 Daftar Transaksi")
    st.dataframe(df, use_container_width=True)

    with st.expander("🗑️ Hapus Transaksi"):
        st.markdown("Pilih ID transaksi yang ingin dihapus.")
        selected_id = st.number_input("ID Transaksi", min_value=1, step=1)
        if st.button("Hapus Sekarang"):
            delete_transaksi(int(selected_id))
            st.success("✅ Transaksi berhasil dihapus.")

# === ANALISIS KEUANGAN ===
def render_financial_analysis(df):
    st.markdown("### 📊 Ringkasan Keuangan")
    total_pemasukan = df[df['kategori'] == 'Pemasukan']['jumlah'].sum()
    total_pengeluaran = df[df['kategori'] == 'Pengeluaran']['jumlah'].sum()
    saldo_akhir = total_pemasukan - total_pengeluaran

    col1, col2, col3 = st.columns(3)
    col1.metric("🟢 Total Pemasukan", f"Rp {total_pemasukan:,.2f}")
    col2.metric("🔴 Total Pengeluaran", f"Rp {total_pengeluaran:,.2f}")
    col3.metric("💰 Saldo Akhir", f"Rp {saldo_akhir:,.2f}")

    st.markdown("---")
    st.markdown("#### 📈 Grafik Berdasarkan Kategori")
    chart_data = df.groupby("kategori")["jumlah"].sum().reset_index()
    st.bar_chart(chart_data, x="kategori", y="jumlah")

# === KALENDER TRANSAKSI ===
def render_calendar_view(df):
    st.markdown("### 📆 Kalender Transaksi")
    df['tanggal'] = pd.to_datetime(df['tanggal'])
    df['tanggal_str'] = df['tanggal'].dt.strftime('%Y-%m-%d')
    df_grouped = df.groupby("tanggal_str").agg({
        "jumlah": "sum",
        "kategori": lambda x: ', '.join(set(x))
    }).reset_index()

    st.dataframe(df_grouped, use_container_width=True)

# === SETTING TAMPILAN UTAMA ===
st.set_page_config(page_title="💰 Finance Tracker", layout="wide")
st.title("💼 Finance Tracker App")

# === SIDEBAR NAVIGASI ===
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2331/2331948.png", width=80)
    st.markdown("## Navigasi")
    menu = st.radio("", [
        "📥 Form Input", 
        "📋 Tabel Transaksi", 
        "📊 Analisis Keuangan", 
        "🗓️ Kalender Transaksi"
    ])
    st.markdown("---")
    st.caption("Made with ❤️ by Ilham")

# === LOAD DATA ===
data_transaksi = pd.DataFrame(get_all_transaksi())

# === RENDER KONTEN SESUAI MENU ===
if menu == "📥 Form Input":
    data = render_form()
    if data:
        insert_transaksi(data)
        st.success("✅ Transaksi berhasil disimpan!")

elif menu == "📋 Tabel Transaksi":
    if data_transaksi.empty:
        st.info("📭 Belum ada transaksi.")
    else:
        render_transaction_table(data_transaksi)

elif menu == "📊 Analisis Keuangan":
    if data_transaksi.empty:
        st.info("📭 Belum ada data untuk analisis.")
    else:
        render_financial_analysis(data_transaksi)

elif menu == "🗓️ Kalender Transaksi":
    if data_transaksi.empty:
        st.info("📭 Belum ada transaksi.")
    else:
        render_calendar_view(data_transaksi)
