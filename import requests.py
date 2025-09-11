import requests
import pandas as pd

API_URLS = [
    "https://bios.kemenkeu.go.id/api2/ws/nextgen/get/pendidikan/layanan/akreditasi_institusi_prodi",
    "https://bios.kemenkeu.go.id/api2/ws/nextgen/get/pendidikan/layanan/alumni",
    "https://bios.kemenkeu.go.id/api2/ws/nextgen/get/pendidikan/layanan/cluster_ptn",
    "https://bios.kemenkeu.go.id/api2/ws/nextgen/get/pendidikan/layanan/ikm_pendidikan",
    "https://bios.kemenkeu.go.id/api2/ws/nextgen/get/pendidikan/layanan/jumlah_dosen_yang_berkegiatan_di_luar_kampus",
    "https://bios.kemenkeu.go.id/api2/ws/nextgen/get/pendidikan/layanan/jumlah_haki",
    "https://bios.kemenkeu.go.id/api2/ws/nextgen/get/pendidikan/layanan/jumlah_karya_tulis_ilmiah_dipublikasikan",
    "https://bios.kemenkeu.go.id/api2/ws/nextgen/get/pendidikan/layanan/jumlah_kegiatan_pengabdian_kepada_masyarakat",
    "https://bios.kemenkeu.go.id/api2/ws/nextgen/get/pendidikan/layanan/jumlah_kerja_sama",
    "https://bios.kemenkeu.go.id/api2/ws/nextgen/get/pendidikan/layanan/jumlah_mahasiswa",
    "https://bios.kemenkeu.go.id/api2/ws/nextgen/get/pendidikan/layanan/jumlah_mahasiswa_berprestasi",
    "https://bios.kemenkeu.go.id/api2/ws/nextgen/get/pendidikan/layanan/jumlah_mahasiswa_yang_berkegiatan_di_luar_kampus",
    "https://bios.kemenkeu.go.id/api2/ws/nextgen/get/pendidikan/layanan/jumlah_mitra_kerjasama_diklat",
    "https://bios.kemenkeu.go.id/api2/ws/nextgen/get/pendidikan/layanan/jumlah_pelatihan_kewirausahaan",
    "https://bios.kemenkeu.go.id/api2/ws/nextgen/get/pendidikan/layanan/jumlah_penerima_beasiswa",
    "https://bios.kemenkeu.go.id/api2/ws/nextgen/get/pendidikan/layanan/jumlah_penerima_beasiswa_ppsdm",
    "https://bios.kemenkeu.go.id/api2/ws/nextgen/get/pendidikan/layanan/jumlah_penerima_kegiatan_pengabdian_pada_masyarakat",
    "https://bios.kemenkeu.go.id/api2/ws/nextgen/get/pendidikan/layanan/jumlah_peserta_diklat",
    "https://bios.kemenkeu.go.id/api2/ws/nextgen/get/pendidikan/layanan/jumlah_peserta_sertifikasi",
    "https://bios.kemenkeu.go.id/api2/ws/nextgen/get/pendidikan/layanan/jumlah_prodi_yang_melakukan_kerjasama_dengan_mitra_dalam_rangka_tri_dharma",
    "https://bios.kemenkeu.go.id/api2/ws/nextgen/get/pendidikan/layanan/jumlah_prodi_yang_menerapkan_pembelajaran_kampus_merdeka",
    "https://bios.kemenkeu.go.id/api2/ws/nextgen/get/pendidikan/layanan/jumlah_produk_inovasi",
    "https://bios.kemenkeu.go.id/api2/ws/nextgen/get/pendidikan/layanan/jumlah_prototipe_industri",
    "https://bios.kemenkeu.go.id/api2/ws/nextgen/get/pendidikan/layanan/jumlah_publikasi_penelitian",
]

BEARER_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL3RyYWluaW5nLWJpb3MyLmtlbWVua2V1LmdvLmlkL2FwaS90b2tlbiIsImlhdCI6MTc1NzQ3MTM1NCwiZXhwIjoxNzU3NTU3NzU0LCJuYmYiOjE3NTc0NzEzNTQsImp0aSI6ImM1ME9sM1hqbmJidEZyMk4iLCJrZHNhdGtlciI6IjQxNTY3MCJ9.8X7iewF0RX0_TaNnv2IHQDXL1-MGYACECuKoNu6jJl0"

def fetch_data(api_url, kdsatker=None):
    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
    }
    payload = {}
    if kdsatker:
        payload["kdsatker"] = kdsatker

    response = requests.post(api_url, headers=headers, data=payload)
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    try:
        kdsatker = input("Enter kdsatker (leave blank to fetch all): ").strip() or None
        all_results = {}

        for url in API_URLS:
            print(f"Fetching from {url} ...")
            try:
                data = fetch_data(url, kdsatker)
                all_results[url.split("/")[-1]] = data
            except Exception as e:
                print(f"Error fetching {url}: {e}")

        # Simpan ke CSV per endpoint
        for key, value in all_results.items():
            df = pd.DataFrame(value.get("data", []))
            filename = f"output_{key}.csv"
            df.to_csv(filename, index=False)
            print(f"Saved {filename} ({len(df)} rows)")

    except Exception as e:
        print("Error:", e)
