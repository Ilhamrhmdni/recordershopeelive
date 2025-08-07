# Struktur awal aplikasi catatan keuangan kompleks dengan analisis
# File: app.py

import streamlit as st
from datetime import date
from supabase_client import supabase
import pandas as pd

st.set_page_config(page_title="📒 Catatan Keuangan Pribadi", page_icon="💰", layout="wide")
st.title("📒 Dashboard Keuangan")

# Ambil data dari Supabase
res = supabase.table("keuangan").select("*").order("tanggal", desc=True).execute()
df = pd.DataFrame(res.data)

if df.empty:
    st.info("Belum ada data keuangan. Silakan input di menu 📥 Input.")
    st.stop()

# Ubah kolom tanggal jadi format datetime
if 'tanggal' in df.columns:
    df['tanggal'] = pd.to_datetime(df['tanggal']).dt.date

# Hitung saldo harian
if 'kategori' in df.columns and 'jumlah' in df.columns:
    df['nilai'] = df.apply(lambda row: row['jumlah'] if row['kategori'] == 'Pemasukan' else -row['jumlah'], axis=1)
    saldo_harian = df.groupby("tanggal")["nilai"].sum().cumsum().reset_index()
else:
    saldo_harian = pd.DataFrame(columns=["tanggal", "nilai"])

# Ringkasan
col1, col2, col3 = st.columns(3)
with col1:
    pemasukan = df[df['kategori'] == 'Pemasukan']['jumlah'].sum()
    st.metric("Total Pemasukan", f"Rp {pemasukan:,.0f}")
with col2:
    pengeluaran = df[df['kategori'] == 'Pengeluaran']['jumlah'].sum()
    st.metric("Total Pengeluaran", f"Rp {pengeluaran:,.0f}")
with col3:
    saldo = pemasukan - pengeluaran
    st.metric("Saldo Saat Ini", f"Rp {saldo:,.0f}")

# Grafik garis saldo harian
import plotly.express as px

st.subheader("📈 Grafik Saldo Harian")
fig = px.line(saldo_harian, x="tanggal", y="nilai", title="Pergerakan Saldo")
st.plotly_chart(fig, use_container_width=True)

# Navigasi ke halaman lain
st.sidebar.title("📁 Navigasi")
st.sidebar.page_link("pages/1_📥_Input.py", label="📥 Input Transaksi")
st.sidebar.page_link("pages/2_📄_Data.py", label="📄 Data Transaksi")
st.sidebar.page_link("pages/3_📊_Analisis.py", label="📊 Analisis Keuangan")
