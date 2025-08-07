import streamlit as st
from database import insert_journal, fetch_all_journals
from datetime import date, time

st.set_page_config(page_title="Jurnal Trading", layout="centered")
st.title("📒 Jurnal Trading Ilham")

menu = st.sidebar.radio("Menu", ["Input Jurnal", "Lihat Jurnal"])

if menu == "Input Jurnal":
    with st.form("jurnal_form"):
        pair = st.text_input("Pair (contoh: XAU/USD)")
        timeframe = st.selectbox("Timeframe", ["5M", "15M", "30M", "1H", "4H", "1D"])
        entry_type = st.radio("Tipe Entry", ["BUY", "SELL"])
        entry_reason = st.text_area("Alasan Entry")
        result = st.radio("Hasil", ["WIN", "LOSS"])
        entry_price = st.number_input("Entry Price", format="%.2f")
        exit_price = st.number_input("Exit Price", format="%.2f")
        sl = st.number_input("Stop Loss", format="%.2f")
        tp = st.number_input("Take Profit", format="%.2f")
        tanggal = st.date_input("Tanggal", value=date.today())
        waktu = st.time_input("Waktu", value=time())

        submitted = st.form_submit_button("Simpan Jurnal")
        if submitted:
            profit_loss = round(exit_price - entry_price, 2) if entry_type == "BUY" else round(entry_price - exit_price, 2)

            data = {
                "pair": pair,
                "timeframe": timeframe,
                "entry_type": entry_type,
                "entry_reason": entry_reason,
                "result": result,
                "entry_price": entry_price,
                "exit_price": exit_price,
                "sl": sl,
                "tp": tp,
                "tanggal": str(tanggal),
                "waktu": str(waktu),
                "profit_loss": profit_loss
            }

            insert_journal(data)
            st.success("✅ Data jurnal berhasil disimpan!")

elif menu == "Lihat Jurnal":
    journals = fetch_all_journals()
    if journals:
        st.dataframe(journals)
    else:
        st.warning("Belum ada data jurnal yang tersimpan.")
