import streamlit as st
from supabase import create_client
from datetime import datetime, date
import pandas as pd
import io

# ---------------- CONFIG ----------------
SUPABASE_URL = "https://nwsjgtrzyrebdaioczhj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im53c2pndHJ6eXJlYmRhaW9jemhqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ1NjM4ODgsImV4cCI6MjA3MDEzOTg4OH0.jxmfTFHp7vSwkzE5dVgw7-WKdgKUTxIsysaeA9DRSCw"
TABLE_NAME = "keuangan"

# Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------- HELPERS (CRUD) ----------------
def insert_transaksi(data: dict):
    try:
        res = supabase.table(TABLE_NAME).insert(data).execute()
        return res
    except Exception as e:
        st.error(f"Gagal menyimpan transaksi: {e}")
        return None

def get_all_transaksi():
    try:
        res = supabase.table(TABLE_NAME).select("*").order("tanggal", desc=False).execute()
        return res.data if res.data else []
    except Exception as e:
        st.error(f"Gagal mengambil data: {e}")
        return []

def delete_transaksi(row_id: int):
    try:
        return supabase.table(TABLE_NAME).delete().eq("id", row_id).execute()
    except Exception as e:
        st.error(f"Gagal menghapus data: {e}")
        return None

def update_transaksi(row_id: int, updated_data: dict):
    try:
        return supabase.table(TABLE_NAME).update(updated_data).eq("id", row_id).execute()
    except Exception as e:
        st.error(f"Gagal memperbarui data: {e}")
        return None

# ---------------- UI COMPONENTS ----------------

def render_form(defaults=None):
    with st.form("form_transaksi"):
        tanggal_val = defaults.get('tanggal') if defaults else date.today()
        if isinstance(tanggal_val, str):
            try:
                tanggal_val = datetime.fromisoformat(tanggal_val).date()
            except:
                tanggal_val = date.today()

        tanggal = st.date_input("Tanggal", value=tanggal_val)
        kategori = st.selectbox("Kategori", ["Pemasukan", "Pengeluaran"], index=0 if not defaults else (0 if defaults.get('kategori')=='Pemasukan' else 1))
        deskripsi = st.text_input("Deskripsi", value=defaults.get('deskripsi') if defaults else "")
        jumlah = st.number_input("Jumlah", min_value=0.0, format="%.2f", value=float(defaults.get('jumlah')) if defaults and defaults.get('jumlah') is not None else 0.0)
        metode = st.selectbox("Metode Pembayaran", ["Cash", "Transfer", "E-Wallet"], index=0 if not defaults else ["Cash","Transfer","E-Wallet"].index(defaults.get('metode')) if defaults and defaults.get('metode') in ["Cash","Transfer","E-Wallet"] else 0)
        submitted = st.form_submit_button("Simpan")

        if submitted:
            payload = {
                "tanggal": tanggal.isoformat(),
                "kategori": kategori,
                "deskripsi": deskripsi,
                "jumlah": float(jumlah),
                "metode": metode
            }
            return payload
    return None


def render_transaction_table(df):
    st.dataframe(df.reset_index(drop=True), use_container_width=True)

    with st.expander("🗑️ Hapus Transaksi"):
        selected_id = st.number_input("ID Transaksi yang ingin dihapus", min_value=1, step=1)
        confirm = st.checkbox("Saya yakin ingin menghapus transaksi ini")
        if st.button("Hapus"):
            if confirm:
                delete_transaksi(int(selected_id))
                st.success("Transaksi berhasil dihapus.")
            else:
                st.warning("Centang kotak konfirmasi sebelum menghapus.")

    with st.expander("✏️ Edit Transaksi"):
        selected_id_edit = st.number_input("ID Transaksi yang ingin diedit", min_value=1, step=1, key="edit_id")
        if st.button("Load Data", key="load_edit"):
            row = supabase.table(TABLE_NAME).select("*").eq("id", int(selected_id_edit)).execute().data
            if row and len(row) > 0:
                row = row[0]
                defaults = row
                edited = render_form(defaults=defaults)
                if edited:
                    update_transaksi(int(selected_id_edit), edited)
                    st.success("Data berhasil diperbarui.")
            else:
                st.error("Data tidak ditemukan untuk ID tersebut.")

# ---------------- ANALYSIS ----------------

def render_financial_analysis(df):
    df['tanggal'] = pd.to_datetime(df['tanggal'])
    total_pemasukan = df[df['kategori'] == 'Pemasukan']['jumlah'].sum()
    total_pengeluaran = df[df['kategori'] == 'Pengeluaran']['jumlah'].sum()
    saldo_akhir = total_pemasukan - total_pengeluaran

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Pemasukan", f"Rp {total_pemasukan:,.2f}")
    col2.metric("Total Pengeluaran", f"Rp {total_pengeluaran:,.2f}")
    col3.metric("Saldo Akhir", f"Rp {saldo_akhir:,.2f}")

    st.subheader("📊 Grafik Berdasarkan Kategori")
    kategori_chart = df.groupby("kategori")["jumlah"].sum().reset_index()
    st.bar_chart(kategori_chart.set_index('kategori'))

    st.subheader("📌 Grafik Berdasarkan Deskripsi (Top 20)")
    deskripsi_chart = df.groupby("deskripsi")["jumlah"].sum().reset_index().sort_values(by="jumlah", ascending=False).head(20)
    st.bar_chart(deskripsi_chart.set_index('deskripsi'))

    st.subheader("📈 Tren Saldo Bulanan")
    df['bulan'] = df['tanggal'].dt.to_period('M').astype(str)
    bulanan = df.groupby('bulan').apply(lambda x: x[x['kategori']=='Pemasukan']['jumlah'].sum() - x[x['kategori']=='Pengeluaran']['jumlah'].sum()).reset_index(name='saldo')
    st.line_chart(bulanan.set_index('bulan'))

# ---------------- CALENDAR VIEW ----------------

def render_calendar_view(df):
    df['tanggal'] = pd.to_datetime(df['tanggal'])
    df['tanggal_str'] = df['tanggal'].dt.strftime('%Y-%m-%d')
    df_grouped = df.groupby("tanggal_str").agg({
        "jumlah": "sum",
        "kategori": lambda x: ', '.join(sorted(set(x)))
    }).reset_index()
    st.dataframe(df_grouped, use_container_width=True)

# ---------------- EXPORT ----------------

def get_download_link_csv(df):
    towrite = io.BytesIO()
    df.to_csv(towrite, index=False)
    towrite.seek(0)
    return towrite

# ---------------- APP LAYOUT ----------------

st.set_page_config(page_title="Finance Tracker", layout="wide")
st.title("💰 Finance Tracker - Versi Lengkap")

with st.sidebar:
    st.title("📘 Finance Menu")
    menu = st.radio("📂 Navigasi", [
        "Home",
        "Tambah Transaksi",
        "Tabel Transaksi",
        "Analisis Keuangan",
        "Kalender Transaksi",
        "Export / Import"
    ])
    st.markdown("---")
    st.caption("🔧 Dibuat oleh Ilham")

# Load data once per run
raw_data = get_all_transaksi()

if menu == "Home":
    st.image("https://i.imgur.com/BXzG7j1.png", width=400)
    st.subheader("Selamat Datang di Aplikasi Finance Tracker 👋")
    st.write("Aplikasi ini membantu kamu mencatat, memantau, dan menganalisis keuangan pribadi secara lebih lengkap.")
    st.write("Fitur: tambah/edit/hapus, filter periode, grafik bulanan, export CSV, dan kalender transaksi.")

elif menu == "Tambah Transaksi":
    st.subheader("📝 Tambah Transaksi")
    data = render_form()
    if data:
        insert_transaksi(data)
        st.success("✅ Transaksi berhasil disimpan!")

elif menu == "Tabel Transaksi":
    st.subheader("📋 Riwayat Transaksi")
    df = pd.DataFrame(raw_data)
    if df.empty:
        st.info("Belum ada data transaksi.")
    else:
        st.write("Filter periode:")
        min_date = pd.to_datetime(df['tanggal']).min().date()
        max_date = pd.to_datetime(df['tanggal']).max().date()
        start_date = st.date_input("Dari", value=min_date, min_value=min_date, max_value=max_date)
        end_date = st.date_input("Sampai", value=max_date, min_value=min_date, max_value=max_date)
        mask = (pd.to_datetime(df['tanggal']).dt.date >= start_date) & (pd.to_datetime(df['tanggal']).dt.date <= end_date)
        df_filtered = df.loc[mask].copy()

        render_transaction_table(df_filtered)

        st.markdown("---")
        st.subheader("📥 Download Data Periode")
        if not df_filtered.empty:
            csv_bytes = get_download_link_csv(df_filtered)
            st.download_button(label="Download CSV", data=csv_bytes, file_name=f"transactions_{start_date}_to_{end_date}.csv", mime='text/csv')
        else:
            st.info("Tidak ada data pada periode yang dipilih.")

elif menu == "Analisis Keuangan":
    st.subheader("📈 Analisis Keuangan")
    df = pd.DataFrame(raw_data)
    if df.empty:
        st.info("Belum ada data untuk dianalisis.")
    else:
        st.write("Filter periode untuk analisis:")
        min_date = pd.to_datetime(df['tanggal']).min().date()
        max_date = pd.to_datetime(df['tanggal']).max().date()
        start_date = st.date_input("Dari", value=min_date, min_value=min_date, max_value=max_date, key='anal_start')
        end_date = st.date_input("Sampai", value=max_date, min_value=min_date, max_value=max_date, key='anal_end')
        mask = (pd.to_datetime(df['tanggal']).dt.date >= start_date) & (pd.to_datetime(df['tanggal']).dt.date <= end_date)
        df_filtered = df.loc[mask].copy()
        if df_filtered.empty:
            st.info("Tidak ada data pada periode yang dipilih.")
        else:
            render_financial_analysis(df_filtered)

elif menu == "Kalender Transaksi":
    st.subheader("📅 Kalender Transaksi")
    df = pd.DataFrame(raw_data)
    if df.empty:
        st.info("Belum ada data transaksi.")
    else:
        render_calendar_view(df)

elif menu == "Export / Import":
    st.subheader("📦 Export / Import Data")
    df = pd.DataFrame(raw_data)
    st.write("Export seluruh data:")
    if df.empty:
        st.info("Belum ada data untuk diexport.")
    else:
        csv_bytes = get_download_link_csv(df)
        st.download_button(label="Download CSV Seluruh Data", data=csv_bytes, file_name="transactions_all.csv", mime='text/csv')

    st.markdown("---")
    st.write("Import CSV (format: tanggal,kategori,deskripsi,jumlah,metode)")
    uploaded = st.file_uploader("Pilih file CSV untuk diimport", type=["csv"])
    if uploaded is not None:
        try:
            df_up = pd.read_csv(uploaded)
            if not set(['tanggal','kategori','deskripsi','jumlah','metode']).issubset(df_up.columns):
                st.error("Format CSV tidak sesuai. Harus ada kolom: tanggal,kategori,deskripsi,jumlah,metode")
            else:
                if st.button("Mulai Import"):
                    successes = 0
                    for _, row in df_up.iterrows():
                        payload = {
                            'tanggal': pd.to_datetime(row['tanggal']).isoformat(),
                            'kategori': str(row['kategori']),
                            'deskripsi': str(row['deskripsi']),
                            'jumlah': float(row['jumlah']),
                            'metode': str(row['metode'])
                        }
                        insert_transaksi(payload)
                        successes += 1
                    st.success(f"Import selesai. {successes} baris berhasil diupload.")
        except Exception as e:
            st.error(f"Gagal membaca file CSV: {e}")

# Footer
st.markdown("---")
st.caption("Tips: pastikan koneksi internet dan konfigurasi Supabase benar. Jika ada error, cek RLS (Row Level Security) di dashboard Supabase.")
