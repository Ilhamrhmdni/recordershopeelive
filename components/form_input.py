# components/form_input.py
import streamlit as st
import datetime

def render_form():
    with st.form(key="form_transaksi"):
        tanggal = st.date_input("Tanggal", datetime.date.today())

        kategori = st.selectbox("Kategori", ["Pemasukan", "Pengeluaran"])

        if kategori == "Pemasukan":
            sub_kategori = st.selectbox("Sub-Kategori", ["Gaji", "Bonus", "Lainnya"])
        else:
            sub_kategori = st.selectbox("Sub-Kategori", ["Makan", "Transportasi", "Tagihan", "Belanja", "Lainnya"])

        jumlah = st.number_input("Jumlah", min_value=0.0, step=1000.0, format="%.2f")

        metode = st.selectbox("Metode Pembayaran", ["Cash", "E-wallet", "Bank"])

        keterangan = st.text_input("Keterangan (opsional)")

        submit = st.form_submit_button("Simpan")

        if submit:
            return {
                "tanggal": str(tanggal),
                "kategori": kategori,
                "sub_kategori": sub_kategori,
                "jumlah": jumlah,
                "metode": metode,
                "keterangan": keterangan,
            }
    return None
