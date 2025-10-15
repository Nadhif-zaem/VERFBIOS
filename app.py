import streamlit as st
import requests
import pandas as pd
import time

# --- CONFIG ---
BASE_URL = "https://bios.kemenkeu.go.id"
AUTH_URL = BASE_URL + "/api2/authenticate"
DATA_URL = BASE_URL + "/api/pengajuan/data"

st.set_page_config(page_title="BIOS Webservice Dashboard", layout="wide")
st.title("📊 BIOS Webservice Dashboard")

# --- SESSION STATE ---
if "token" not in st.session_state:
    st.session_state.token = None
if "data" not in st.session_state:
    st.session_state.data = None

# --- SIDEBAR STRUCTURE ---
with st.sidebar:
    st.header("🔐 1️⃣ Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_btn = st.button("🚀 Login ke BIOS")

    if login_btn:
        if not username or not password:
            st.error("Harap isi username dan password!")
        else:
            with st.spinner("Mengautentikasi ke BIOS..."):
                try:
                    res = requests.post(AUTH_URL, json={"username": username, "password": password}, timeout=20)
                    if res.status_code == 200:
                        data = res.json()
                        # token bisa berada di key 'token', 'data.token', atau 'access_token'
                        token = (
                            data.get("token")
                            or data.get("access_token")
                            or (data.get("data", {}).get("token") if "data" in data else None)
                        )
                        if token:
                            st.session_state.token = token
                            st.success("✅ Login berhasil!")
                        else:
                            st.error("Login berhasil tapi token tidak ditemukan.")
                            st.json(data)
                    else:
                        st.error(f"Gagal login (HTTP {res.status_code})")
                        st.text(res.text[:400])
                except Exception as e:
                    st.error(f"Gagal menghubungi server: {e}")

    st.divider()
    st.header("⏱️ 2️⃣ Extra Miles")
    from_date = st.text_input("Tanggal Awal (YYYY/MM/DD)")
    to_date = st.text_input("Tanggal Akhir (YYYY/MM/DD)"
