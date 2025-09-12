import pandas as pd
import streamlit as st
import requests
import os

# API config
API_URL = "https://bios.kemenkeu.go.id/api2/ws/nextgen/get/keuangan/saldo/saldo_operasional"
BEARER_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL2Jpb3Mua2VtZW5rZXUuZ28uaWQvYXBpMi9hdXRoZW50aWNhdGUiLCJpYXQiOjE3NTc1NzE5MDksImV4cCI6MTc1NzY1ODMwOSwibmJmIjoxNzU3NTcxOTA5LCJqdGkiOiJWS3MzR2JSYktjOXh4ZHVyIiwic3ViIjoiMzQ1MzgwIiwicHJ2IjoiMjNiZDVjODk0OWY2MDBhZGIzOWU3MDFjNDAwODcyZGI3YTU5NzZmNyJ9.sYrsL6QwkWiq98EAdFKexj2RpjE3z2mH4xmOxYjZ6y4"
CSV_FILE = "saldo_data.csv"

# Fetch one page
def fetch_page(page=1, kdsatker=None):
    headers = {"Authorization": f"Bearer {BEARER_TOKEN}"}
    payload = {"kdsatker": kdsatker} if kdsatker else {}

    response = requests.post(f"{API_URL}?page={page}", headers=headers, data=payload)
    response.raise_for_status()
    return response.json()

# Fetch all pages silently
def fetch_all_data(kdsatker=None):
    all_data = []

    first_result = fetch_page(1, kdsatker)
    first_data = first_result.get("data", {})

    total_pages = int(first_data.get("pageCount", 0))
    if total_pages == 0:
        return pd.DataFrame()

    all_data.extend(first_data.get("datas", []))

    for page in range(2, total_pages + 1):
        result = fetch_page(page, kdsatker)
        page_data = result.get("data", {})
        all_data.extend(page_data.get("datas", []))

    df = pd.DataFrame(all_data)

    # Convert saldo_akhir to numeric
    if "saldo_akhir" in df.columns:
        df["saldo_akhir"] = pd.to_numeric(df["saldo_akhir"], errors="coerce")

    # Convert tgl_transaksi to datetime
    if "tgl_transaksi" in df.columns:
        df["tgl_transaksi"] = pd.to_datetime(df["tgl_transaksi"], errors="coerce")

    return df

# Main Streamlit app
def main():
    st.title("Saldo Operasional Dashboard")

    kdsatker = st.text_input("Enter kdsatker (leave blank for all):")

    if st.button("Fetch & Show Data"):
        df = fetch_all_data(kdsatker)

        if not df.empty:
            df.to_csv(CSV_FILE, index=False)
            st.success(f"Data fetched successfully: {len(df)} rows saved to {CSV_FILE}")

            # Extract available years
            if "tgl_transaksi" in df.columns:
                df["year"] = df["tgl_transaksi"].dt.year
                years = sorted(df["year"].dropna().unique())
                selected_year = st.selectbox("Select Year", years)

                # Filter data by year
                df = df[df["year"] == selected_year]

            # Print full table per kdbank + interactive chart
            st.subheader(f"Saldo Data per kdbank ({selected_year})")
            for bank, g in df.groupby("kdbank"):
                st.write(f"### kdbank: {bank}")
                st.dataframe(g)

                # Plot saldo trend
                if "tgl_transaksi" in g.columns and "saldo_akhir" in g.columns:
                    g_sorted = g.sort_values("tgl_transaksi")
                    st.line_chart(
                        g_sorted.set_index("tgl_transaksi")["saldo_akhir"],
                        use_container_width=True
                    )

        else:
            st.warning("No data found.")

if __name__ == "__main__":
    main()