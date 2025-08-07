# components/transaction_table.py
import streamlit as st
import pandas as pd
from utils.data_handler import delete_transaction

def render_transaction_table(df):
    st.subheader("📊 Tabel Transaksi")

    # Filter
    col1, col2, col3 = st.columns(3)
    with col1:
        tanggal_filter = st.date_input("Filter Tanggal", value=None)
    with col2:
        kategori_filter = st.selectbox("Filter Kategori", ["Semua", "Pemasukan", "Pengeluaran"])
    with col3:
        metode_filter = st.selectbox("Filter Metode Pembayaran", ["Semua", "Cash", "E-wallet", "Bank"])

    # Terapkan filter
    if tanggal_filter:
        df = df[df["tanggal"] == str(tanggal_filter)]
    if kategori_filter != "Semua":
        df = df[df["kategori"] == kategori_filter]
    if metode_filter != "Semua":
        df = df[df["metode"] == metode_filter]

    if df.empty:
        st.info("Tidak ada data.")
        return

    df_display = df.copy()
    df_display["jumlah"] = df_display["jumlah"].apply(lambda x: f"Rp {x:,.2f}")

    st.dataframe(df_display, use_container_width=True)

    # Aksi hapus
    for idx, row in df.iterrows():
        with st.expander(f"📝 Detail Transaksi {idx+1}"):
            st.write(row)
            if st.button(f"Hapus Transaksi {idx+1}", key=f"delete_{idx}"):
                delete_transaction(row["id"])
                st.success("Data berhasil dihapus.")
                st.experimental_rerun()
