import streamlit as st
from utils.data_handler import insert_transaksi, get_all_transaksi
from components.form_input import render_form
from components.transaction_table import render_transaction_table
from components.financial_analysis import render_financial_analysis
from components.calendar_view import render_calendar_view

# Setup halaman
st.set_page_config(page_title="Finance Tracker", layout="wide")
st.title("💰 Finance Tracker App")

# Sidebar navigasi
menu = st.sidebar.radio("Navigasi", ["Form Input", "Tabel Transaksi", "Analisis Keuangan", "Kalender Transaksi"])

# Tampilan berdasarkan menu
if menu == "Form Input":
    st.subheader("📝 Tambah Transaksi")
    data = render_form()
    if data:
        insert_transaksi(data)
        st.success("Transaksi berhasil disimpan!")

elif menu == "Tabel Transaksi":
    st.subheader("📋 Riwayat Transaksi")
    df = get_all_transaksi()
    if not df:
        st.info("Belum ada data transaksi.")
    else:
        render_transaction_table(df)

elif menu == "Analisis Keuangan":
    st.subheader("📊 Analisis Keuangan")
    df = get_all_transaksi()
    if not df:
        st.info("Belum ada data untuk dianalisis.")
    else:
        render_financial_analysis(df)

elif menu == "Kalender Transaksi":
    st.subheader("📅 Kalender Transaksi")
    df = get_all_transaksi()
    if not df:
        st.info("Belum ada data transaksi.")
    else:
        render_calendar_view(df)
