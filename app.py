# app.py
import streamlit as st
import pandas as pd
from services import db
from components import form_input, charts

st.set_page_config(page_title="Catatan Keuangan Pribadi", layout="wide")
st.title("📒 Catatan Keuangan Pribadi")

with st.sidebar:
    st.header("Tambah Transaksi")
    new_data = form_input.render_form()
    if new_data:
        db.insert_transaksi(new_data)
        st.success("Transaksi berhasil ditambahkan!")

# Tampilkan data
st.subheader("📋 Riwayat Transaksi")
data = db.get_all_transaksi()
st.dataframe(data, use_container_width=True)

# Chart ringkas
st.subheader("📈 Grafik Ringkas")
charts.render_summary_charts(data)
