import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="📊 Dashboard Affiliate", layout="wide")
st.title("📊 Dashboard Analisis Data Afiliasi Shopee")

# Upload file
uploaded_file = st.file_uploader("Upload file CSV laporan afiliasi", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)

        # Bersihkan kolom waktu jika ada
        if 'Waktu Pemesanan' in df.columns:
            df['Waktu Pemesanan'] = pd.to_datetime(df['Waktu Pemesanan'])
            df['Tanggal'] = df['Waktu Pemesanan'].dt.date

        st.success("File berhasil dimuat!")
        
        # Tampilkan preview
        st.subheader("🔍 Preview Data")
        st.dataframe(df.head())

        # Filter hanya pesanan selesai
        canceled_orders = df[df['Status Pesanan'] == 'Dibatalkan']
        completed_orders = df[df['Status Pesanan'] == 'Selesai']

        # Statistik dasar
        total_orders = len(df)
        completed_count = len(completed_orders)
        canceled_count = len(canceled_orders)
        total_commission = df['Komisi XTRA Produk(Rp)'].sum()
        avg_commission = df[df['Komisi XTRA Produk(Rp)'] > 0]['Komisi XTRA Produk(Rp)'].mean()

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Pesanan", total_orders)
        col2.metric("Pesanan Selesai", completed_count)
        col3.metric("Pesanan Dibatalkan", canceled_count)
        col4.metric("Total Komisi", f"Rp{total_commission:,.0f}")

        # Tren pesanan per hari
        if 'Tanggal' in df.columns:
            daily_orders = df.groupby('Tanggal').size().reset_index(name='Jumlah')
            fig = px.line(daily_orders, x='Tanggal', y='Jumlah', title='📈 Tren Jumlah Pesanan Per Hari')
            st.plotly_chart(fig)

        # Produk terlaris
        top_products = df.groupby('Nama Barange')['Jumlah'].sum().sort_values(ascending=False).head(10)
        fig = px.bar(top_products, x=top_products.index, y=top_products.values, title='🏆 Produk Terlaris')
        st.plotly_chart(fig)

        # Alasan pembatalan
        if 'Alasan Pembatalan / Penolakan' in df.columns:
            cancel_reasons = canceled_orders['Alasan Pembatalan / Penolakan'].value_counts()
            fig = px.pie(cancel_reasons, values=cancel_reasons.values, names=cancel_reasons.index, title='🚫 Alasan Pembatalan Pesanan')
            st.plotly_chart(fig)

        # Download hasil analisis
        st.download_button(
            label="⬇️ Download Hasil Analisis",
            data=df.to_csv(index=False).encode('utf-8'),
            file_name="analisis_pesanan.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"Error membaca file: {e}")
else:
    st.info("Silakan upload file CSV untuk mulai analisis.")
