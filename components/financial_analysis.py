# components/financial_analysis.py
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_handler import load_data

def render_analysis():
    st.subheader("📈 Analisis Keuangan")

    df = load_data()
    if df.empty:
        st.info("Belum ada data transaksi.")
        return

    df["tanggal"] = pd.to_datetime(df["tanggal"])
    df.sort_values("tanggal", inplace=True)

    pemasukan = df[df["kategori"] == "Pemasukan"]["jumlah"].sum()
    pengeluaran = df[df["kategori"] == "Pengeluaran"]["jumlah"].sum()
    saldo = pemasukan - pengeluaran

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Pemasukan", f"Rp {pemasukan:,.2f}")
    col2.metric("Total Pengeluaran", f"Rp {pengeluaran:,.2f}")
    col3.metric("Saldo Akhir", f"Rp {saldo:,.2f}")

    # Grafik Saldo Harian
    df["netto"] = df.apply(lambda row: row["jumlah"] if row["kategori"] == "Pemasukan" else -row["jumlah"], axis=1)
    df_saldo = df.groupby("tanggal")["netto"].sum().cumsum().reset_index(name="saldo")

    fig_line = px.line(df_saldo, x="tanggal", y="saldo", title="Saldo Harian")
    st.plotly_chart(fig_line, use_container_width=True)

    # Grafik Pengeluaran per Kategori
    df_pengeluaran = df[df["kategori"] == "Pengeluaran"]
    if not df_pengeluaran.empty:
        fig_bar = px.bar(df_pengeluaran.groupby("sub_kategori")["jumlah"].sum().reset_index(),
                         x="sub_kategori", y="jumlah", title="Pengeluaran per Kategori")
        st.plotly_chart(fig_bar, use_container_width=True)

    # Pie Chart Metode Pembayaran
    fig_pie = px.pie(df, names="metode", title="Distribusi Metode Pembayaran", values="jumlah")
    st.plotly_chart(fig_pie, use_container_width=True)
