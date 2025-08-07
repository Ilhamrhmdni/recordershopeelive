# components/calendar_view.py
import streamlit as st
import pandas as pd
from utils.data_handler import load_data

def render_calendar():
    st.subheader("📅 Kalender Transaksi")

    df = load_data()
    if df.empty:
        st.info("Belum ada data transaksi.")
        return

    df["tanggal"] = pd.to_datetime(df["tanggal"])
    df.sort_values("tanggal", inplace=True)

    tanggal_unik = df["tanggal"].dt.date.unique()

    for tgl in tanggal_unik:
        st.markdown(f"### {tgl.strftime('%d %B %Y')}")
        data_hari_ini = df[df["tanggal"].dt.date == tgl]
        
        for _, row in data_hari_ini.iterrows():
            warna = "green" if row["kategori"] == "Pemasukan" else "red"
            st.markdown(
                f"<div style='border-left: 5px solid {warna}; padding: 0.5rem; margin-bottom: 0.5rem;'>"
                f"<strong>{row['kategori']} - {row['sub_kategori']}</strong><br>"
                f"Jumlah: Rp {row['jumlah']:,.2f}<br>"
                f"Metode: {row['metode']}<br>"
                f"{'Keterangan: ' + row['keterangan'] if row['keterangan'] else ''}"
                f"</div>", unsafe_allow_html=True
            )
