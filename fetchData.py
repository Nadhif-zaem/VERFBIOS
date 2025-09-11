
import requests
import pandas as pd

API_URL = "https://training-bios2.kemenkeu.go.id/api/get/data/keuangan/saldo/saldo_operasional"

BEARER_TOKEN =  "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL3RyYWluaW5nLWJpb3MyLmtlbWVua2V1LmdvLmlkL2FwaS90b2tlbiIsImlhdCI6MTc1NzQ3MTM1NCwiZXhwIjoxNzU3NTU3NzU0LCJuYmYiOjE3NTc0NzEzNTQsImp0aSI6ImM1ME9sM1hqbmJidEZyMk4iLCJrZHNhdGtlciI6IjQxNTY3MCJ9.8X7iewF0RX0_TaNnv2IHQDXL1-MGYACECuKoNu6jJl0"

def fetch_page(page=1):
    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json"
    }
    response = requests.post(f"{API_URL}?page={page}", headers=headers)
    response.raise_for_status()
    return response.json()

def get_all_data():
    all_data = []

    # First request
    first_result = fetch_page(1)
    first_data = first_result.get("data", {})

    if not first_data:
        raise ValueError("Response does not contain 'data'")

    total_pages = int(first_data.get("pageCount", 0))
    if total_pages == 0:
        raise ValueError("Could not determine total pages from API response")

    print(f"Total pages: {total_pages}")

    all_data.extend(first_data.get("datas", []))

    # Loop through remaining pages
    for page in range(2, total_pages + 1):
        print(f"Fetching page {page}...")
        result = fetch_page(page)
        page_data = result.get("data", {})
        all_data.extend(page_data.get("datas", []))

    return all_data

if __name__ == "__main__":
    try:
        data = get_all_data()

        # Convert to DataFrame
        df = pd.DataFrame(data)

        # Save to CSV
        df.to_csv("output.csv", index=False)

        print("\n=== Final Result Saved ===")
        print(f"Total items fetched: {len(df)}")
        print("Data saved to output.csv")

    except Exception as e:
        print("Error:", e)