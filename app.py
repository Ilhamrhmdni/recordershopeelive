import streamlit as st
from supabase import create_client
from datetime import datetime
import pandas as pd

# --- KONFIGURASI SUPABASE ---
SUPABASE_URL = "https://nwsjgtrzyrebdaioczhj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im53c2pndHJ6eXJlYmRhaW9jemhqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ1NjM4ODgsImV4cCI6MjA3MDEzOTg4OH0.jxmfTFHp7vSwkzE5dVgw7-WKdgKUTxIsysaeA9DRSCw"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
TABLE_NAME = "keuangan"
PROFILE_TABLE = "profiles"

# --- BUAT ADMIN OTOMATIS JIKA BELUM ADA ---
def create_admin_if_not_exists():
    email = "administrator@example.com"
    password = "akukaya"
    # Cek apakah sudah ada user admin
    existing = supabase.table(PROFILE_TABLE).select("*").eq("email", email).execute().data
    if not existing:
        # Buat user auth di Supabase
        auth_res = supabase.auth.sign_up({"email": email, "password": password})
        if auth_res.user:
            uid = auth_res.user.id
            supabase.table(PROFILE_TABLE).insert({
                "id": uid,
                "email": email,
                "role": "admin"
            }).execute()
            st.success("✅ Admin berhasil dibuat!")
        else:
            st.error("❌ Gagal membuat admin. Cek konfigurasi Supabase.")

# --- LOGIN ---
def login(email, password):
    try:
        auth_res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if auth_res.user:
            user_data = supabase.table(PROFILE_TABLE).select("*").eq("id", auth_res.user.id).execute().data
            if user_data:
                return {"id": auth_res.user.id, "email": email, "role": user_data[0]['role']}
        return None
    except Exception as e:
        st.error(f"Login error: {e}")
        return None

# --- CRUD TRANSAKSI ---
def insert_transaksi(data: dict):
    return supabase.table(TABLE_NAME).insert(data).execute()

def get_all_transaksi(user_id=None, role="user"):
    query = supabase.table(TABLE_NAME).select("*").order("tanggal", desc=False)
    if role != "admin":
        query = query.eq("user_id", user_id)
    return query.execute().data

def delete_transaksi(row_id: int, user_id=None, role="user"):
    query = supabase.table(TABLE_NAME).delete().eq("id", row_id)
    if role != "admin":
        query = query.eq("user_id", user_id)
    return query.execute()

# --- FORM INPUT TRANSAKSI ---
def render_form(user_id):
    with st.form("form_transaksi"):
        tanggal = st.date_input("Tanggal", value=datetime.today())
        kategori = st.selectbox("Kategori", ["Pemasukan", "Pengeluaran"])
        deskripsi = st.text_input("Deskripsi")
        jumlah = st.number_input("Jumlah", min_value=0.0, format="%.2f")
        metode = st.selectbox("Metode Pembayaran", ["Cash", "Transfer", "E-Wallet"])
        submitted = st.form_submit_button("Simpan")

        if submitted:
            return {
                "user_id": user_id,
                "tanggal": tanggal.isoformat(),
                "kategori": kategori,
                "deskripsi": deskripsi,
                "jumlah": jumlah,
                "metode": metode
            }
    return None

# --- MENU ADMIN: KELOLA USER ---
def kelola_user():
    st.subheader("👤 Kelola User")
    with st.form("form_user"):
        email = st.text_input("Email User")
        password = st.text_input("Password", type="password")
        role = st.selectbox("Role", ["user", "admin"])
        submitted = st.form_submit_button("Tambah User")
        if submitted:
            auth_res = supabase.auth.sign_up({"email": email, "password": password})
            if auth_res.user:
                supabase.table(PROFILE_TABLE).insert({
                    "id": auth_res.user.id,
                    "email": email,
                    "role": role
                }).execute()
                st.success(f"✅ User {email} berhasil dibuat!")

    # List user
    users = supabase.table(PROFILE_TABLE).select("*").execute().data
    st.table(pd.DataFrame(users))

# --- APP ---
st.set_page_config(page_title="Finance Tracker", layout="wide")

if "user" not in st.session_state:
    create_admin_if_not_exists()
    st.title("🔑 Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user = login(email, password)
        if user:
            st.session_state.user = user
            st.rerun()
        else:
            st.error("Login gagal! Periksa email dan password.")
else:
    user = st.session_state.user
    st.sidebar.write(f"👋 {user['email']} ({user['role']})")
    menu = st.sidebar.radio("Menu", ["Home", "Tambah Transaksi", "Tabel Transaksi", "Analisis Keuangan", "Kelola User" if user['role'] == 'admin' else None])

    if menu == "Home":
        st.image("https://i.imgur.com/BXzG7j1.png", width=400)
        st.subheader("Selamat Datang di Aplikasi Finance Tracker 👋")

    elif menu == "Tambah Transaksi":
        st.subheader("📝 Tambah Transaksi")
        data = render_form(user['id'])
        if data:
            insert_transaksi(data)
            st.success("✅ Transaksi berhasil disimpan!")

    elif menu == "Tabel Transaksi":
        st.subheader("📋 Riwayat Transaksi")
        df = pd.DataFrame(get_all_transaksi(user['id'], user['role']))
        if df.empty:
            st.info("Belum ada data transaksi.")
        else:
            st.dataframe(df, use_container_width=True)

    elif menu == "Analisis Keuangan":
        st.subheader("📈 Analisis Keuangan")
        df = pd.DataFrame(get_all_transaksi(user['id'], user['role']))
        if df.empty:
            st.info("Belum ada data.")
        else:
            total_pemasukan = df[df['kategori'] == 'Pemasukan']['jumlah'].sum()
            total_pengeluaran = df[df['kategori'] == 'Pengeluaran']['jumlah'].sum()
            saldo_akhir = total_pemasukan - total_pengeluaran
            st.metric("Pemasukan", f"Rp {total_pemasukan:,.2f}")
            st.metric("Pengeluaran", f"Rp {total_pengeluaran:,.2f}")
            st.metric("Saldo", f"Rp {saldo_akhir:,.2f}")

    elif menu == "Kelola User" and user['role'] == 'admin':
        kelola_user()
