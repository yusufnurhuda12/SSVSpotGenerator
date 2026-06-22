# Rencana Implementasi: Fitur Lanjutan SSV Spot Checker (Super KMZ Tool)

Rencana ini memuat langkah-langkah implementasi fitur tingkat lanjut (*Advanced RF Engineering UX/UI*) yang telah kita diskusikan sebelumnya untuk meningkatkan kapabilitas analitik dan fungsionalitas visual web aplikasi.

## User Review Required
> [!IMPORTANT]
> Mohon di-review kelima fitur di bawah ini. Fitur mana saja yang ingin diprioritaskan atau di-drop? 
> Harap dicatat bahwa implementasi fitur PDF Report membutuhkan penambahan *library* eksternal.

## Open Questions
> [!WARNING]  
> 1. Apakah kita perlu mempertahankan tema "Dark Mode" mutlak pada PDF Report yang di-generate, atau lebih baik *clean white* agar hemat tinta bila diprint?
> 2. Untuk fitur *Distance Measuring*, apakah Anda ingin toleransi standar jarak otomatis diukur dari *Center Site* (Menara) atau antara sesama titik tes?

## Proposed Changes

---

### 1. Peta Interaktif & Pengendalian Layer (Folium Map Upgrade)

Meningkatkan kapabilitas visual peta web agar tim lapangan (RF Engineer) bisa memilah dan mengukur visualisasi sebelum men-*download* KMZ.

#### [MODIFY] [streamlit_app.py](file:///c:/Users/fairytale/.gemini/antigravity-ide/scratch/kmz-generator/streamlit_app.py)
*   **Layer Controls**: Menambahkan `folium.LayerControl()` agar pengguna dapat menghidupkan/mematikan tampilan Sektor (Poligon), Ring Radius, dan Garis Tengah Azimuth secara terpisah melalui panel *checkbox* di pojok peta.
*   **Live Toggle Satelit**: Menginjeksi parameter `folium.TileLayer('google_satellite')` berdampingan dengan `CartoDB dark_matter`. *Engineer* dapat men-toggle tampilan gedung/pohon vs tema gelap secara *live*.
*   **Interactive Distance Measuring**: Menambahkan *plugin* `folium.plugins.MeasureControl` ke dalam *instance* peta. Pengguna akan memiliki ikon penggaris untuk mengklik titik mana saja di layar web dan menghitung jarak aktual dalam meter.

---

### 2. Mini Analytics & Radar Azimuth Plot

Memberikan intelijen tambahan (Overview Analytics) berdasarkan data titik tes dan sektor.

#### [MODIFY] [streamlit_app.py](file:///c:/Users/fairytale/.gemini/antigravity-ide/scratch/kmz-generator/streamlit_app.py)
*   **Library Tambahan**: Menggunakan `plotly.express` atau `altair` bawaan Streamlit untuk merender grafik polar (*Radar Plot*).
*   **Visualisasi Sektor**: Menampilkan *Radar Plot* di sebelah / di bawah input teks. Plot ini akan memvisualisasikan ke arah mana (Azimuth) sektor-sektor memancar (contoh: 0°, 120°, 240°).
*   **Delta Distance (Status)**: Algoritma tambahan akan membandingkan jarak "Distance to BTS" yang diklaim di tabel dengan "Jarak Garis Lurus aktual (Haversine Formula)" berdasarkan *Latitude/Longitude*. Jika meleset > 10%, sistem akan memunculkan *badge* *"Warning: Koordinat tidak akurat"*.

---

### 3. Auto-Generate PDF / Excel Report

Sistem cetak laporan profesional "sekali klik" (*One-Click Report*) langsung dari data yang diproses.

#### [NEW] [report_generator.py](file:///c:/Users/fairytale/.gemini/antigravity-ide/scratch/kmz-generator/report_generator.py)
*   Modul terpisah untuk menyusun dan mengekspor dokumen laporan menggunakan `pdfkit`, `reportlab`, atau `pandas.to_excel`.
*   Akan menarik *snapshot* titik-titik tes dan memasukkannya ke dalam format *template* PDF "Drive Test / SSV Report" korporat (berisi tabel metadata Site, *Status Pass/Fail* tiap sektor, dan *Screenshot Map* secara statis).

#### [MODIFY] [streamlit_app.py](file:///c:/Users/fairytale/.gemini/antigravity-ide/scratch/kmz-generator/streamlit_app.py)
*   Menambahkan tombol sekunder: **"📑 Download PDF Report"** tepat di sebelah tombol **"🚀 Download File KMZ"**.
*   Menambahkan logika `st.status` untuk merender PDF di *backend* jika tombol tersebut ditekan.

---

## Verification Plan

### Manual Verification
1.  **Map Interaction Check**: *Deploy* secara lokal dan tes mengubah layer antara Satelit dan *Dark Mode*. Mengukur secara bebas jarak rumah sekitar menggunakan alat ukur penggaris (*Measure Control*).
2.  **Analytics Check**: Memasukkan koordinat palsu (berjarak 10km dari *center site*). Memastikan peringatan *Delta Distance Warning* menyala, menandakan proteksi data korup berjalan dengan baik.
3.  **Download PDF Check**: Menekan tombol unduh PDF, lalu memastikan dokumen yang dihasilkan dapat dibaca di seluruh sistem operasi (iOS/Windows) dengan *formatting* tabel yang rapi.
