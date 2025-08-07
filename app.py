import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px
from datetime import datetime

# Inisialisasi Supabase
@st.cache_resource
def init_supabase():
    url = st.secrets="supabase_url"
    key = st.secrets="supabase_key"
    return create_client(url, key)

supabase = init_supabase()

st.set_page_config(page_title="Catatan Keuangan Pribadi", layout="wide")

# Navigasi
page = st.sidebar.selectbox("📌 Navigasi", [
    "🏠 Dashboard",
    "🧾 Input Transaksi",
    "📄 Data Transaksi",
    "📊 Analisis Keuangan",
    "📅 Kalender Keuangan"
])

# Helper untuk ambil data
@st.cache_data

def load_data():
    response = supabase.table("finance_data").select("*").execute()
    return pd.DataFrame(response.data)

# ---------------------- 🏠 Dashboard ---------------------- #
if page == "🏠 Dashboard":
    st.title("📊 Dashboard Keuangan Harian")
    df = load_data()

    if df.empty:
        st.info("Belum ada data.")
    else:
        df["tanggal"] = pd.to_datetime(df["tanggal"])
        total_in = df[df.kategori == "Pemasukan"]["jumlah"].sum()
        total_out = df[df.kategori == "Pengeluaran"]["jumlah"].sum()
        saldo = total_in - total_out

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Pemasukan", f"Rp {total_in:,.0f}")
        col2.metric("Total Pengeluaran", f"Rp {total_out:,.0f}")
        col3.metric("Saldo Saat Ini", f"Rp {saldo:,.0f}")

        df_harian = df.groupby("tanggal")["jumlah"].apply(lambda x: x.sum()).reset_index()
        st.plotly_chart(px.line(df_harian, x="tanggal", y="jumlah", title="Total Transaksi Harian"))

# ---------------------- 🧾 Input Transaksi ---------------------- #
elif page == "🧾 Input Transaksi":
    st.title("🧾 Input Data Keuangan")
    with st.form("input_form"):
        tanggal = st.date_input("Tanggal", datetime.today())
        kategori = st.selectbox("Kategori", ["Pemasukan", "Pengeluaran"])
        subkategori = st.selectbox("Sub-kategori", ["Gaji", "Makan", "Transportasi", "Belanja", "Tagihan", "Investasi", "Lainnya"])
        jumlah = st.number_input("Jumlah", min_value=0)
        metode = st.selectbox("Metode Pembayaran", ["Cash", "E-wallet", "Bank"])
        keterangan = st.text_input("Keterangan")
        submit = st.form_submit_button("Simpan")

        if submit:
            data = {
                "tanggal": str(tanggal),
                "kategori": kategori,
                "subkategori": subkategori,
                "jumlah": jumlah,
                "metode": metode,
                "keterangan": keterangan,
            }
            supabase.table("finance_data").insert(data).execute()
            st.success("Transaksi berhasil disimpan!")

# ---------------------- 📄 Data Transaksi ---------------------- #
elif page == "📄 Data Transaksi":
    st.title("📄 Semua Data Transaksi")
    df = load_data()
    if df.empty:
        st.info("Belum ada data.")
    else:
        with st.expander("🔍 Filter"):
            f_tgl = st.date_input("Filter Tanggal", [])
            f_kat = st.multiselect("Filter Kategori", df.kategori.unique())
            f_metode = st.multiselect("Metode Pembayaran", df.metode.unique())

        if f_tgl:
            df = df[df.tanggal.isin([str(t) for t in f_tgl])]
        if f_kat:
            df = df[df.kategori.isin(f_kat)]
        if f_metode:
            df = df[df.metode.isin(f_metode)]

        st.dataframe(df.sort_values("tanggal", ascending=False), use_container_width=True)

# ---------------------- 📊 Analisis Keuangan ---------------------- #
elif page == "📊 Analisis Keuangan":
    st.title("📊 Analisis Keuangan")
    df = load_data()
    if df.empty:
        st.info("Belum ada data.")
    else:
        df["tanggal"] = pd.to_datetime(df["tanggal"])
        saldo_harian = df.groupby("tanggal").apply(
            lambda x: x[x.kategori == "Pemasukan"]["jumlah"].sum() - x[x.kategori == "Pengeluaran"]["jumlah"].sum()
        ).cumsum().reset_index(name="saldo")

        pengeluaran_kat = df[df.kategori == "Pengeluaran"].groupby("subkategori")["jumlah"].sum().reset_index()
        metode_chart = df.groupby("metode")["jumlah"].sum().reset_index()

        st.plotly_chart(px.line(saldo_harian, x="tanggal", y="saldo", title="Saldo Per Hari"))
        st.plotly_chart(px.bar(pengeluaran_kat, x="subkategori", y="jumlah", title="Pengeluaran per Kategori"))
        st.plotly_chart(px.pie(metode_chart, names="metode", values="jumlah", title="Distribusi Metode Pembayaran"))

# ---------------------- 📅 Kalender Keuangan ---------------------- #
elif page == "📅 Kalender Keuangan":
    st.title("📅 Kalender Keuangan")
    df = load_data()
    if df.empty:
        st.info("Belum ada data.")
    else:
        df["tanggal"] = pd.to_datetime(df["tanggal"])
        df_day = df.groupby("tanggal")["jumlah"].sum().reset_index()
        fig = px.density_heatmap(df_day, x="tanggal", y=["Jumlah"]*len(df_day), z="jumlah", nbinsx=30, title="Heatmap Pengeluaran/Pemasukan")
        st.plotly_chart(fig)
