import streamlit as st
import pandas as pd
import requests
import time
from urllib.parse import unquote

# =========================
# CONFIG
# =========================
BASE_URL = "https://bios.kemenkeu.go.id"
AUTH_URL = BASE_URL + "/api2/authenticate"
API_URL = BASE_URL + "/api/pengajuan/data"
PAGE_SIZE = 1000
SLEEP_BETWEEN = 0.6

st.set_page_config(page_title="Status Webservice BIOS", layout="wide")
st.title("📊 Status Webservice BIOS Kemenkeu")

st.markdown("""
Masukkan **username** dan **password BIOS**, serta **rentang tanggal** untuk mengambil data dari API.  
Aplikasi ini akan login otomatis dan menampilkan hasil dalam tabel interaktif.
""")

# =========================
# USER INPUTS
# =========================
with st.sidebar:
    st.header("🔐 Login BIOS API")
    username = st.text_input("Username", placeholder="Masukkan username", key="username")
    password = st.text_input("Password", placeholder="Masukkan password", type="password", key="password")
    st.markdown("---")
    st.header("📅 Rentang Tanggal")
    from_date = st.text_input("Tanggal Awal (YYYY/MM/DD)")
    to_date = st.text_input("Tanggal Akhir (YYYY/MM/DD)")
    run_button = st.button("🚀 Ambil Data")

# =========================
# MAIN LOGIC
# =========================
if run_button:
    if not (username and password and from_date and to_date):
        st.error("⚠️ Harap isi username, password, dan tanggal terlebih dahulu.")
        st.stop()

    # --- Step 1: Authenticate ---
    st.info("🔑 Mengautentikasi ke BIOS API ...")
    try:
        auth_response = requests.post(AUTH_URL, json={"username": username, "password": password}, timeout=30)
    except Exception as e:
        st.error(f"Gagal menghubungi server autentikasi: {e}")
        st.stop()

    if auth_response.status_code != 200:
        st.error(f"Login gagal. Kode status: {auth_response.status_code}\n\n{auth_response.text[:300]}")
        st.stop()

    try:
        token_data = auth_response.json()
    except Exception:
        st.error("Respons login bukan JSON valid.")
        st.stop()

    # ambil token
    token = token_data.get("token") or token_data.get("access_token")
    if not token:
        st.error("Token tidak ditemukan di respons autentikasi.")
        st.json(token_data)
        st.stop()

    st.success("✅ Login berhasil! Token diperoleh.")
    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {token}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": BASE_URL + "/webservice/pengajuan",
    })

    # --- Step 2: Fetch Data ---
    progress = st.progress(0)
    all_records = []
    start = 0
    page = 1
    st.info(f"📡 Mengambil data dari API {API_URL} ...")

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
            r = session.get(API_URL, params=params, timeout=60)
        except Exception as e:
            st.error(f"Request gagal: {e}")
            break

        if r.status_code != 200:
            st.error(f"Server error ({r.status_code}): {r.text[:300]}")
            break

        try:
            js = r.json()
        except Exception as e:
            st.error(f"Gagal parse JSON: {e}")
            break

        records = js.get("data") or js.get("records") or js.get("aaData") or []
        if not records:
            st.info("✅ Tidak ada data tambahan. Selesai.")
            break

        all_records.extend(records)
        progress.progress(min(1.0, page * 0.05))

        if len(records) < PAGE_SIZE:
            break

        start += PAGE_SIZE
        page += 1
        time.sleep(SLEEP_BETWEEN)

    if not all_records:
        st.warning("Tidak ada data yang berhasil diambil.")
        st.stop()

    df = pd.DataFrame(all_records)

    # --- Step 3: Transformasi Data ---
    lower_cols = {c.lower(): c for c in df.columns}
    def find_col(names):
        for n in names:
            if n.lower() in lower_cols:
                return lower_cols[n.lower()]
        return None

    kdsatker_col = find_col(["kdsatker", "kode_satker"])
    nmsatker_col = find_col(["nmsatker", "nama_satker"])
    nmstatus_col = find_col(["nmstatus", "status", "status_webservice"])
    ts_col = find_col(["updated_at","tgl_update","created_at","tgl_pengajuan","tgl"])

    if not kdsatker_col: df["kdsatker"] = None; kdsatker_col = "kdsatker"
    if not nmsatker_col: df["nmsatker"] = None; nmsatker_col = "nmsatker"
    if not nmstatus_col: df["nmstatus"] = None; nmstatus_col = "nmstatus"

    keep_cols = [kdsatker_col, nmsatker_col, nmstatus_col]
    if ts_col: keep_cols.append(ts_col)
    df2 = df[keep_cols].rename(columns={
        kdsatker_col: "kdsatker",
        nmsatker_col: "nmsatker",
        nmstatus_col: "nmstatus",
        ts_col: "ts" if ts_col else None
    })

    for c in ["kdsatker","nmsatker","nmstatus"]:
        df2[c] = df2[c].astype(str).str.strip().replace({"": None, "nan": None})

    df_clean = df2.dropna(subset=["kdsatker","nmsatker","nmstatus"])

    if "ts" in df_clean.columns:
        df_clean["ts_parsed"] = pd.to_datetime(df_clean["ts"], errors="coerce")
        idx = df_clean.groupby(["kdsatker","nmsatker"])["ts_parsed"].idxmax()
        deduped = df_clean.loc[idx].reset_index(drop=True)
    else:
        deduped = df_clean.groupby(["kdsatker","nmsatker"], as_index=False).last()

    def compute_nilai(s):
        if not isinstance(s, str): return 0
        s = s.strip().lower()
        if "development" in s and "verif" not in s: return 10
        if "verifikasi dev" in s: return 20
        if "request sk prod" in s: return 50
        if "verifikasi prod" in s: return 60
        return 0

    deduped["Nilai"] = deduped["nmstatus"].apply(compute_nilai)
    deduped["Capaian"] = deduped["Nilai"] * 0.2

    final_df = pd.DataFrame({
        "No": range(1, len(deduped) + 1),
        "Kode Satker": deduped["kdsatker"],
        "Nama Satker": deduped["nmsatker"],
        "Status Webservice": deduped["nmstatus"],
        "Nilai": deduped["Nilai"],
        "Capaian": deduped["Capaian"]
    })

    st.success(f"✅ Data berhasil diambil ({len(final_df)} baris).")
    st.dataframe(final_df, use_container_width=True)

    st.download_button(
        label="💾 Download Hasil Excel",
        data=final_df.to_excel(index=False, engine='openpyxl'),
        file_name="hasil_status_ws.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
