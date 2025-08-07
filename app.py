import streamlit as st
import pandas as pd
from supabase_client import supabase
from datetime import date

st.title("📒 Catatan Keuangan Pribadi")

# Form input
with st.form("form_keuangan"):
    tanggal = st.date_input("Tanggal", date.today())
    kategori = st.selectbox("Kategori", ["Pemasukan", "Pengeluaran"])
    jumlah = st.number_input("Jumlah (Rp)", min_value=0)
    keterangan = st.text_input("Keterangan")
    submit = st.form_submit_button("Simpan")

    if submit:
        data = {
            "tanggal": tanggal.isoformat(),
            "kategori": kategori,
            "jumlah": jumlah,
            "keterangan": keterangan
        }
        supabase.table("keuangan").insert(data).execute()
        st.success("Catatan berhasil disimpan!")

# Tampilkan data
st.subheader("📊 Riwayat Keuangan")
res = supabase.table("keuangan").select("*").order("tanggal", desc=True).execute()
df = pd.DataFrame(res.data)
st.dataframe(df)

# Ringkasan
if not df.empty:
    total_masuk = df[df['kategori'] == "Pemasukan"]['jumlah'].sum()
    total_keluar = df[df['kategori'] == "Pengeluaran"]['jumlah'].sum()
    sisa = total_masuk - total_keluar

    st.metric("Total Pemasukan", f"Rp {total_masuk:,.0f}")
    st.metric("Total Pengeluaran", f"Rp {total_keluar:,.0f}")
    st.metric("Sisa Saldo", f"Rp {sisa:,.0f}")
