import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="📊 Dashboard Afiliasi", layout="wide")
st.title("📊 Dashboard Analisis Data Afiliasi Shopee")

# Upload file
uploaded_file = st.file_uploader("Upload file CSV laporan afiliasi", type=["csv"])

if uploaded_file is not None:
    try:
        # Baca CSV
        df = pd.read_csv(uploaded_file)

        # Bersihkan kolom waktu jika ada
        if 'Waktu Pemesanan' in df.columns:
            df['Waktu Pemesanan'] = pd.to_datetime(df['Waktu Pemesanan'], errors='coerce')
            df['Tanggal'] = df['Waktu Pemesanan'].dt.date
            df['Jam'] = df['Waktu Pemesanan'].dt.hour
            df['Hari'] = df['Waktu Pemesanan'].dt.day_name()

        st.success("File berhasil dimuat!")

        # Tampilkan preview
        st.subheader("🔍 Preview Data")
        st.dataframe(df.head())

        # Statistik Dasar
        total_orders = len(df)
        completed_orders = df[df['Status Pesanan'] == 'Selesai']
        canceled_orders = df[df['Status Pesanan'] == 'Dibatalkan']
        pending_orders = df[df['Status Pesanan'] == 'Tertunda']

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Pesanan", total_orders)
        col2.metric("Pesanan Selesai", len(completed_orders))
        col3.metric("Pesanan Dibatalkan", len(canceled_orders))
        col4.metric("Pesanan Tertunda", len(pending_orders))

        # Konversi
        conversion_rate = len(completed_orders) / total_orders * 100
        st.write(f"✅ **Persentase Konversi**: {conversion_rate:.2f}%")

        # Tren Waktu
        st.subheader("📈 Tren Waktu Pesanan")

        time_col1, time_col2 = st.columns(2)

        with time_col1:
            daily_orders = df.groupby('Tanggal').size().reset_index(name='Jumlah')
            fig_daily = px.line(daily_orders, x='Tanggal', y='Jumlah', title='📅 Jumlah Pesanan Harian')
            st.plotly_chart(fig_daily)

        with time_col2:
            hour_counts = df['Jam'].value_counts().sort_index()
            fig_hour = px.bar(hour_counts, x=hour_counts.index, y=hour_counts.values, title='⏰ Jumlah Pesanan Per Jam')
            st.plotly_chart(fig_hour)

        day_counts = df['Hari'].value_counts()
        fig_day = px.pie(day_counts, names=day_counts.index, values=day_counts.values, title='📆 Hari dengan Pesanan Terbanyak')
        st.plotly_chart(fig_day)

        # Analisis Produk
        st.subheader("🏆 Produk Terlaris & Komisi")

        top_products = df.groupby('Nama Barange')['Jumlah'].sum().sort_values(ascending=False).head(10)
        fig_top_products = px.bar(top_products, x=top_products.index, y=top_products.values, title='🛍️ Produk Terlaris')
        st.plotly_chart(fig_top_products)

        df['Komisi XTRA Produk(Rp)'] = pd.to_numeric(df['Komisi XTRA Produk(Rp)'], errors='coerce')
        product_commission = df.groupby('Nama Barange')['Komisi XTRA Produk(Rp)'].sum().sort_values(ascending=False).head(10)
        fig_product_commission = px.bar(product_commission, x=product_commission.index, y=product_commission.values,
                                        title='💰 Komisi Tertinggi per Produk')
        st.plotly_chart(fig_product_commission)

        # Pendapatan & Komisi
        st.subheader("💸 Ringkasan Pendapatan")

        total_commission_xtra = df['Komisi XTRA Produk(Rp)'].sum()
        avg_commission = df['Komisi XTRA Produk(Rp)'].mean()
        total_shopee_commission = df['Biaya Manajemen MCN(Rp)'].sum() if 'Biaya Manajemen MCN(Rp)' in df.columns else 0

        col5, col6, col7 = st.columns(3)
        col5.metric("Total Komisi XTRA (Rp)", f"{total_commission_xtra:,.0f}")
        col6.metric("Rata-rata Komisi (Rp)", f"{avg_commission:,.0f}")
        col7.metric("Total Biaya Manajemen MCN (Rp)", f"{total_shopee_commission:,.0f}")

        # Toko / Merchant
        st.subheader("🏢 Analisis Toko")

        top_sellers = df['Nama Toko'].value_counts().head(10)
        fig_top_sellers = px.bar(top_sellers, x=top_sellers.index, y=top_sellers.values, title='🛒 Toko Paling Sering Dipromosikan')
        st.plotly_chart(fig_top_sellers)

        seller_commission = df.groupby('Nama Toko')['Komisi XTRA Produk(Rp)'].sum().sort_values(ascending=False).head(10)
        fig_seller_commission = px.bar(seller_commission, x=seller_commission.index, y=seller_commission.values,
                                       title='💰 Komisi Tertinggi per Toko')
        st.plotly_chart(fig_seller_commission)

        # Platform / Sumber Trafik
        if 'Platform' in df.columns:
            st.subheader("🌐 Analisis Platform Asal Pesanan")
            platform_counts = df['Platform'].value_counts()
            fig_platform = px.pie(platform_counts, names=platform_counts.index, values=platform_counts.values,
                                  title='📱 Distribusi Pesanan Berdasarkan Platform')
            st.plotly_chart(fig_platform)

        # Download hasil
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
