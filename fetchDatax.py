import requests
import pandas as pd

API_URL = "https://training-bios2.kemenkeu.go.id/api/get/data/keuangan/saldo/saldo_operasional"

BEARER_TOKEN =  "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL3RyYWluaW5nLWJpb3MyLmtlbWVua2V1LmdvLmlkL2FwaS90b2tlbiIsImlhdCI6MTc1NzQ3MTM1NCwiZXhwIjoxNzU3NTU3NzU0LCJuYmYiOjE3NTc0NzEzNTQsImp0aSI6ImM1ME9sM1hqbmJidEZyMk4iLCJrZHNhdGtlciI6IjQxNTY3MCJ9.8X7iewF0RX0_TaNnv2IHQDXL1-MGYACECuKoNu6jJl0"

def fetch_page(page=1, kdsatker=None):
    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
    }

    # Form-data style body (like Insomnia/Postman)
    payload = {}
    if kdsatker:
        payload["kdsatker"] = kdsatker

    response = requests.post(f"{API_URL}?page={page}", headers=headers, data=payload)
    response.raise_for_status()
    return response.json()


def get_all_data(kdsatker=None):
    all_data = []

    # First request
    first_result = fetch_page(1, kdsatker)
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
        result = fetch_page(page, kdsatker)
        page_data = result.get("data", {})
        all_data.extend(page_data.get("datas", []))

    return all_data


if __name__ == "__main__":
    try:
        # Ask user for kdsatker
        kdsatker = input("Enter kdsatker (leave blank to fetch all): ").strip() or None

        data = get_all_data(kdsatker)

        # Convert to DataFrame
        df = pd.DataFrame(data)

        # Save to CSV (filename includes kdsatker if provided)
        filename = f"output_{kdsatker}.csv" if kdsatker else "output.csv"
        df.to_csv(filename, index=False)

        print("\n=== Final Result Saved ===")
        print(f"Total items fetched: {len(df)}")
        print(f"Data saved to {filename}")

    except Exception as e:
        print("Error:", e)