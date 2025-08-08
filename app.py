import streamlit as st
from supabase import create_client
from datetime import datetime
import pandas as pd

# --- Konfigurasi Supabase ---
SUPABASE_URL = "https://nwsjgtrzyrebdaioczhj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im53c2pndHJ6eXJlYmRhaW9jemhqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ1NjM4ODgsImV4cCI6MjA3MDEzOTg4OH0.jxmfTFHp7vSwkzE5dVgw7-WKdgKUTxIsysaeA9DRSCw"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- State ---
if "user" not in st.session_state:
    st.session_state.user = None
if "role" not in st.session_state:
    st.session_state.role = None

# --- AUTH ---
def login(email, password):
    res = supabase.auth.sign_in_with_password({"email": email, "password": password})
    if res.user:
        st.session_state.user = res.user
        profile = supabase.table("profiles").select("*").eq("id", res.user.id).execute()
        if profile.data:
            st.session_state.role = profile.data[0]["role"]
        else:
            st.session_state.role = "user"
        return True
    return False

def register(email, password):
    res = supabase.auth.sign_up({"email": email, "password": password})
    if res.user:
        supabase.table("profiles").insert({
            "id": res.user.id,
            "email": email,
            "role": "user"
        }).execute()
        return True
    return False

def logout():
    supabase.auth.sign_out()
    st.session_state.user = None
    st.session_state.role = None

# --- CRUD Keuangan ---
def insert_transaksi(data):
    return supabase.table("keuangan").insert(data).execute()

def get_transaksi():
    return supabase.table("keuangan").select("*").eq("user_id", st.session_state.user.id).order("tanggal", desc=False).execute().data

def delete_transaksi(row_id):
    return supabase.table("keuangan").delete().eq("id", row_id).execute()

# --- Form Transaksi ---
def render_form():
    with st.form("form_transaksi"):
        tanggal = st.date_input("Tanggal", value=datetime.today())
        kategori = st.selectbox("Kategori", ["Pemasukan", "Pengeluaran"])
        deskripsi = st.text_input("Deskripsi")
        jumlah = st.number_input("Jumlah", min_value=0.0, format="%.2f")
        metode = st.selectbox("Metode Pembayaran", ["Cash", "Transfer", "E-Wallet"])
        submitted = st.form_submit_button("Simpan")
        if submitted:
            return {
                "user_id": st.session_state.user.id,
                "tanggal": tanggal.isoformat(),
                "kategori": kategori,
                "deskripsi": deskripsi,
                "jumlah": jumlah,
                "metode": metode
            }
    return None

# --- Admin Panel ---
def admin_panel():
    st.subheader("👑 Admin Panel")
    users = supabase.table("profiles").select("*").execute().data
    df = pd.DataFrame(users)
    st.dataframe(df)

    # Promote user
    non_admins = [u for u in users if u["role"] != "admin"]
    if non_admins:
        email_list = {u["email"]: u["id"] for u in non_admins}
        selected_email = st.selectbox("Pilih User", list(email_list.keys()))
        if st.button("Jadikan Admin"):
            supabase.table("profiles").update({"role": "admin"}).eq("id", email_list[selected_email]).execute()
            st.success(f"{selected_email} sekarang menjadi Admin!")
    else:
        st.info("Semua user sudah admin.")

# --- Layout ---
st.set_page_config(page_title="Finance Tracker", layout="wide")

if st.session_state.user is None:
    st.title("🔑 Login / Register")
    tab1, tab2 = st.tabs(["Login", "Register"])
    with tab1:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if login(email, password):
                st.experimental_rerun()
            else:
                st.error("Login gagal.")
    with tab2:
        email_r = st.text_input("Email ", key="email_reg")
        password_r = st.text_input("Password ", type="password", key="pass_reg")
        if st.button("Register"):
            if register(email_r, password_r):
                st.success("Registrasi berhasil, silakan login.")
            else:
                st.error("Registrasi gagal.")
else:
    with st.sidebar:
        st.write(f"👋 {st.session_state.user.email}")
        menu = st.radio("Menu", ["Tambah Transaksi", "Tabel Transaksi", "Analisis Keuangan", "Kalender Transaksi"] + (["Admin Panel"] if st.session_state.role == "admin" else []))
        if st.button("Logout"):
            logout()
            st.experimental_rerun()

    if menu == "Tambah Transaksi":
        st.subheader("📝 Tambah Transaksi")
        data = render_form()
        if data:
            insert_transaksi(data)
            st.success("✅ Transaksi berhasil disimpan!")

    elif menu == "Tabel Transaksi":
        st.subheader("📋 Riwayat Transaksi")
        df = pd.DataFrame(get_transaksi())
        if df.empty:
            st.info("Belum ada data transaksi.")
        else:
            st.dataframe(df)

    elif menu == "Analisis Keuangan":
        df = pd.DataFrame(get_transaksi())
        if df.empty:
            st.info("Belum ada data.")
        else:
            total_pemasukan = df[df['kategori'] == 'Pemasukan']['jumlah'].sum()
            total_pengeluaran = df[df['kategori'] == 'Pengeluaran']['jumlah'].sum()
            saldo_akhir = total_pemasukan - total_pengeluaran
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Pemasukan", f"Rp {total_pemasukan:,.2f}")
            col2.metric("Total Pengeluaran", f"Rp {total_pengeluaran:,.2f}")
            col3.metric("Saldo Akhir", f"Rp {saldo_akhir:,.2f}")

    elif menu == "Kalender Transaksi":
        df = pd.DataFrame(get_transaksi())
        if df.empty:
            st.info("Belum ada data transaksi.")
        else:
            df['tanggal'] = pd.to_datetime(df['tanggal'])
            df_grouped = df.groupby(df['tanggal'].dt.strftime('%Y-%m-%d')).agg({"jumlah": "sum"}).reset_index()
            st.dataframe(df_grouped)

    elif menu == "Admin Panel" and st.session_state.role == "admin":
        admin_panel()
