import streamlit as st
from supabase import create_client, Client
from datetime import datetime
import pandas as pd

# Konfigurasi Supabase
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# Fungsi validasi
def semua_wajib_diisi(tanggal, kategori, jenis, metode, jumlah):
    return all([tanggal, kategori, jenis, metode, jumlah > 0])

# Fungsi tambah data

def render_form():
    st.subheader("📝 Tambah Transaksi")

    with st.form("form_transaksi"):
        tanggal = st.date_input("Tanggal", value=datetime.today())
        kategori = st.selectbox("Kategori", ["Pemasukan", "Pengeluaran"])
        jenis = st.selectbox("Jenis", ["Umum", "Gaji", "Investasi", "Belanja", "Lainnya"])
        metode = st.selectbox("Metode Pembayaran", ["Cash", "Transfer", "E-Wallet"])
        jumlah = st.number_input("Jumlah", min_value=0.0, format="%.2f")
        keterangan = st.text_area("Keterangan")
        submitted = st.form_submit_button("Simpan")

        if submitted:
            if not semua_wajib_diisi(tanggal, kategori, jenis, metode, jumlah):
                st.warning("Mohon lengkapi semua field wajib.")
                return

            data = {
                "tanggal": tanggal.isoformat(),
                "kategori": kategori,
                "jenis": jenis,
                "metode": metode,
                "jumlah": jumlah,
                "keterangan": keterangan
            }

            response = supabase.table("keuangan").insert(data).execute()

            if response.error:
                st.error(f"Terjadi kesalahan: {response.error.message}")
            else:
                st.success("Transaksi berhasil disimpan!")

# Fungsi edit data

def render_edit_form(row):
    st.subheader("✏️ Edit Transaksi")

    with st.form(f"edit_form_{row['id']}"):
        tanggal = st.date_input("Tanggal", datetime.fromisoformat(row['tanggal']))
        kategori = st.selectbox("Kategori", ["Pemasukan", "Pengeluaran"], index=0 if row['kategori'] == "Pemasukan" else 1)
        jenis = st.selectbox("Jenis", ["Umum", "Gaji", "Investasi", "Belanja", "Lainnya"], index=["Umum", "Gaji", "Investasi", "Belanja", "Lainnya"].index(row['jenis']))
        metode = st.selectbox("Metode Pembayaran", ["Cash", "Transfer", "E-Wallet"], index=["Cash", "Transfer", "E-Wallet"].index(row['metode']))
        jumlah = st.number_input("Jumlah", min_value=0.0, format="%.2f", value=float(row['jumlah']))
        keterangan = st.text_area("Keterangan", value=row['keterangan'])
        update_btn = st.form_submit_button("Update")

        if update_btn:
            if not semua_wajib_diisi(tanggal, kategori, jenis, metode, jumlah):
                st.warning("Mohon lengkapi semua field wajib.")
                return

            updated_data = {
                "tanggal": tanggal.isoformat(),
                "kategori": kategori,
                "jenis": jenis,
                "metode": metode,
                "jumlah": jumlah,
                "keterangan": keterangan
            }

            response = supabase.table("keuangan").update(updated_data).eq("id", row["id"]).execute()

            if response.error:
                st.error(f"Gagal update: {response.error.message}")
            else:
                st.success("Data berhasil diperbarui.")

# Tampilan utama

st.set_page_config(page_title="Finance Tracker", layout="wide")
st.title("💰 Finance Tracker App")

menu = st.sidebar.radio("📌 Navigasi", [
    "📥 Form Input", 
    "📋 Tabel Transaksi"
])

if menu == "📥 Form Input":
    render_form()

elif menu == "📋 Tabel Transaksi":
    st.subheader("📋 Riwayat Transaksi")
    response = supabase.table("keuangan").select("*").order("tanggal", desc=True).execute()

    if response.error:
        st.error("Gagal mengambil data.")
    else:
        data = response.data
        if not data:
            st.info("Belum ada data transaksi.")
        else:
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)

            for row in data:
                with st.expander(f"{row['tanggal']} - {row['kategori']} - Rp{row['jumlah']:,.2f}"):
                    st.write(f"**Jenis:** {row['jenis']}")
                    st.write(f"**Metode:** {row['metode']}")
                    st.write(f"**Jumlah:** Rp{row['jumlah']:,.2f}")
                    st.write(f"**Keterangan:** {row['keterangan']}")

                    if st.button("Edit", key=f"edit_{row['id']}"):
                        render_edit_form(row)
