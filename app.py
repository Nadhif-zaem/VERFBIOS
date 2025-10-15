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
    to_date = st.text_input("Tanggal Akhir (YYYY/MM/DD)")
    fetch_btn = st.button("📡 Ambil Data")

    st.divider()
    st.header("📋 3️⃣ Tampil Data")
    show_data_btn = st.button("📊 Tampilkan Data")

# --- FETCH DATA LOGIC ---
if fetch_btn:
    if not st.session_state.token:
        st.error("Kamu belum login! Silakan login terlebih dahulu di sidebar.")
    elif not from_date or not to_date:
        st.error("Harap isi tanggal awal dan akhir.")
    else:
        with st.spinner("Mengambil data dari BIOS..."):
            session = requests.Session()
            session.headers.update({
                "Authorization": f"Bearer {st.session_state.token}",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "X-Requested-With": "XMLHttpRequest"
            })

            PAGE_SIZE = 1000
            all_records = []
            page = 1
            start = 0
            while True:
                params = {
                    "draw": page,
                    "start": start,
                    "length": PAGE_SIZE,
                    "from_date": from_date,
                    "to_date": to_date,
                    "kdsatker": "",
                    "status": ""
                }
                try:
                    r = session.get(DATA_URL, params=params, timeout=60)
                except Exception as e:
                    st.error(f"Request gagal: {e}")
                    break

                if r.status_code == 401:
                    st.error("❌ 401 Unauthorized — Token tidak valid atau kadaluarsa.")
                    break

                if r.status_code != 200:
                    st.error(f"Server error ({r.status_code})")
                    st.text(r.text[:500])
                    break

                js = r.json()
                records = js.get("data") or js.get("records") or js.get("aaData") or []
                if not records:
                    st.info("✅ Tidak ada data tambahan, selesai.")
                    break

                all_records.extend(records)
                if len(records) < PAGE_SIZE:
                    break
                page += 1
                start += PAGE_SIZE
                time.sleep(0.5)

            if all_records:
                df = pd.DataFrame(all_records)
                st.session_state.data = df
                st.success(f"✅ Data berhasil diambil ({len(df)} baris).")
            else:
                st.warning("Tidak ada data yang diambil.")

# --- DISPLAY DATA ---
if show_data_btn:
    if st.session_state.data is None or st.session_state.data.empty:
        st.warning("Belum ada data yang diambil. Klik 'Ambil Data' di sidebar terlebih dahulu.")
    else:
        df = st.session_state.data

        st.subheader("📊 Data Hasil Pengambilan")
        st.dataframe(df, use_container_width=True, height=500)

        # Tombol download Excel
        to_excel = df.to_excel(index=False, engine='openpyxl')
        st.download_button(
            label="💾 Download sebagai Excel",
            data=to_excel,
            file_name="hasil_bios.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
