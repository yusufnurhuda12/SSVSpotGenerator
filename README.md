# 📡 SSV Spot Generator & Checker

Aplikasi berbasis web interaktif yang dibangun menggunakan [Streamlit](https://streamlit.io/). Aplikasi ini dirancang khusus untuk mempermudah pekerjaan *engineer* telekomunikasi dalam merender file KMZ Sektoral secara instan, serta memvalidasi titik uji lapangan (*Single Site Verification*).

## ✨ Fitur Utama
1. **📡 SSV Spot Generator**: Merender file KMZ Sektoral secara instan dan dinamis berdasarkan data site dari Google Sheets (termasuk pembuatan poligon radius sektor, garis azimuth, dan penanda jarak).
2. **📑 KMZ for ATP**: Menghasilkan file KMZ khusus untuk kebutuhan ATP (*Acceptance Test Procedure*). Pada mode ini, titik-titik Spot SSV dihilangkan sehingga *output* menjadi lebih bersih sesuai dengan format ATP.
3. **🎯 SSV Spot Checker**: Memvalidasi titik tes lapangan secara *real-time*. Anda cukup melakukan *copy-paste* data tabel pengujian dari Excel. Sistem akan memetakan koordinat ke *Live Interactive Map*, serta menghitung metrik jarak aktual (Haversine) dan memvisualisasikan Radar Azimuth.

## 🚀 Panduan Menjalankan Secara Lokal

### 1. Prasyarat Sistem
Pastikan komputer Anda sudah terpasang Python (disarankan versi 3.8 atau lebih baru).

### 2. Instalasi Dependency
Buka terminal/CMD, arahkan ke folder *project* ini, lalu jalankan perintah berikut untuk meng-install semua *library* pendukung:
```bash
pip install -r requirements.txt
```

### 3. Menjalankan Aplikasi
Ketik perintah ini di terminal untuk menjalankan *server* lokal Streamlit:
```bash
streamlit run streamlit_app.py
```
Aplikasi akan secara otomatis terbuka di browser Anda (biasanya di alamat `http://localhost:8501`).

## 📁 Struktur Direktori
*   `streamlit_app.py` - File utama (*entry point*) untuk menjalankan seluruh UI, logika *map rendering*, dan pembuatan file KMZ.
*   `report_generator.py` - Modul khusus pendukung untuk melakukan ekspor hasil validasi ke format dokumen PDF.
*   `requirements.txt` - Daftar *library* (seperti `streamlit`, `simplekml`, `folium`, dll) yang dibutuhkan agar aplikasi ini dapat berjalan dengan sempurna.

## 🛡️ Catatan Tambahan
Data yang digunakan untuk pemetaan ditarik secara langsung (*live sync*) dari Google Sheets publik. Jika ingin menyesuaikan sumber data, Anda bisa mengganti URL di dalam variabel `SHEET_URL` pada file `streamlit_app.py`.
