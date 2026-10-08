> **English summary**
>
> **The problem:** Every spot point and KMZ file used to be created manually — drawn one by one in QGIS. Slow, error-prone, and every team waited on whoever could operate the desktop GIS.
>
> **What I built:** A production web app (Streamlit) that automates the whole workflow end to end. Site data syncs live from the existing database via Google Sheets; the app processes it with Python (geospatial math, coordinate validation) and serves KMZ coverage maps, sector polygons, and ATP-ready exports instantly — so every team can pull what they need in real time, no GIS expertise required.
>
> **Stack:** Python · Streamlit · Shapely/PyProj/Folium · Google Sheets API · PDF reporting. Built solo, deployed, and used in production by technical field teams.

---

# SSV Spot Generator & Checker

Aplikasi web interaktif (Streamlit) untuk engineer telekomunikasi: merender file KMZ sektoral secara instan dan memvalidasi titik uji lapangan (Single Site Verification).

## Kenapa aplikasi ini dibuat

Pembuatan titik spot dan file KMZ sebelumnya dikerjakan manual — digambar satu per satu di QGIS. Prosesnya lambat, rawan salah, dan semua tim harus menunggu orang yang bisa mengoperasikan GIS desktop.

Aplikasi ini mengotomatiskan seluruh alur: data site tersinkron langsung dari database (Google Sheets), diolah dengan Python, dan disajikan sebagai KMZ siap unduh — realtime, tanpa perlu keahlian GIS.

## Fitur

- **SSV Spot Generator** — Merender KMZ sektoral secara instan dari data Google Sheets: poligon radius sektor, garis azimuth, dan penanda jarak.
- **KMZ for ATP** — Menghasilkan KMZ khusus Acceptance Test Procedure (titik spot dihilangkan agar output bersih sesuai format ATP).
- **SSV Spot Checker** — Validasi titik uji lapangan secara realtime: paste data tabel dari Excel, sistem memetakan koordinat ke peta interaktif, menghitung jarak aktual (Haversine), dan memvisualisasikan radar azimuth. Hasil dapat diekspor ke PDF.

## Cara menjalankan

**Prasyarat:** Python 3.8+

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Buka `http://localhost:8501` di browser.

## Struktur project

| File | Fungsi |
| ---- | ------ |
| `streamlit_app.py` | Entry point: UI, rendering peta, dan pembuatan KMZ |
| `report_generator.py` | Ekspor hasil validasi ke PDF |
| `requirements.txt` | Daftar dependency |

## Catatan

Data pemetaan disinkron langsung (live) dari Google Sheets publik. Untuk mengganti sumber data, ubah variabel `SHEET_URL` di `streamlit_app.py`.
