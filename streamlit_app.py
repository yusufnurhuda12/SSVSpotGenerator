import streamlit as st
import pandas as pd
import numpy as np
import math
import simplekml
import zipfile
import sys
import os
import csv
import io
import sys
import os
from datetime import datetime
from shapely.geometry import Polygon
from pyproj import Transformer
import folium
from folium import Element
from folium.plugins import MeasureControl, LocateControl
from streamlit_folium import st_folium
import plotly.express as px
from geopy.distance import geodesic
from report_generator import generate_pdf

# ==============================
# KONFIGURASI WEB
# ==============================
st.set_page_config(page_title="SSV Spot Checker", page_icon="📡", layout="centered")

# Inject Custom CSS for Premium Tool Look
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');

    /* Global Font & Background */
    html, body, .stApp {
        font-family: 'Outfit', sans-serif;
    }
    .stApp {
        background: radial-gradient(circle at 50% 0%, #1e1b4b 0%, #0f172a 60%, #020617 100%);
        color: #e2e8f0;
    }
    
    /* Animated Glowing Title */
    h1 {
        text-align: center;
        background: linear-gradient(135deg, #00f2fe, #4facfe, #00f2fe);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
        font-size: 3.5rem !important;
        letter-spacing: -1px;
        margin-bottom: 0px !important;
        padding-bottom: 0px !important;
        animation: shine 3s linear infinite;
    }
    @keyframes shine {
        to { background-position: 200% center; }
    }
    
    .subtitle {
        text-align: center;
        color: #94a3b8;
        font-size: 1.1rem;
        font-weight: 300;
        margin-bottom: 25px;
    }
    
    /* Tombol utama (Download & Button) */
    .stButton>button[kind="primary"], .stDownloadButton>button[kind="primary"] {
        background: linear-gradient(90deg, #3b82f6, #8b5cf6) !important;
        border: none !important;
        border-radius: 12px !important;
        color: white !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        transition: transform 0.2s, box-shadow 0.2s !important;
    }
    .stButton>button[kind="primary"]:hover, .stDownloadButton>button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px -10px rgba(139, 92, 246, 0.5);
    }
    
    /* Kontainer modern */
    .glass-card {
        background: rgba(30, 41, 59, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
    }
</style>
""", unsafe_allow_html=True)

# URL CSV
SHEET_URL = "https://docs.google.com/spreadsheets/d/1Yscupy_kQJzFBLOv_2lS0u2J-fKi5XqFoCyjRFXDlLA/export?format=csv&gid=118124849"

# ==============================
# FUNGSI CLEANSING & PULL DATA
# ==============================
@st.cache_data(ttl=600)
def load_and_clean_data(url):
    df_sumber = pd.read_csv(url)
    df_sumber.columns = df_sumber.columns.str.replace('\n', ' ', regex=False).str.replace(' +', ' ', regex=True).str.strip()

    kolom_wajib = [
        'Site ID Surge', 'Site Name Surge', 'Longitude', 'Latitude', 'Azimuth',
        'Ant Height', 'H Beamwidth', 'Power', 'A Gain', 'Freq', 'Band', 'PCI', 'Cell Name'
    ]
    df_target = pd.DataFrame(columns=kolom_wajib)
    df_target['Site ID Surge'] = df_sumber['Site ID Surge']
    df_target['Site Name Surge'] = df_sumber['Site Name Surge']
    df_target['Longitude'] = pd.to_numeric(df_sumber['Longitude'], errors='coerce')
    df_target['Latitude'] = pd.to_numeric(df_sumber['Latitude'], errors='coerce')
    
    if 'PCI' in df_sumber.columns:
        df_target['PCI'] = df_sumber['PCI']
    else:
        df_target['PCI'] = '-'
        
    if 'Cell Name' in df_sumber.columns:
        df_target['Cell Name'] = df_sumber['Cell Name']
    else:
        df_target['Cell Name'] = '-'

    if 'AzimuthReview' in df_sumber.columns:
        az_review = pd.to_numeric(df_sumber['AzimuthReview'], errors='coerce')
        az_biasa = pd.to_numeric(df_sumber['Azimuth'], errors='coerce')
        
        # Cek per site, apakah site tersebut memiliki setidaknya satu nilai Azimuth Review yang valid
        has_review = az_review.groupby(df_sumber['Site ID Surge']).transform(lambda x: x.notna().any())
        
        # Jika site punya review, pakai az_review (walaupun ada NaN, biar sektor berkurang).
        # Jika tidak punya review sama sekali, pakai az_biasa.
        df_target['Azimuth'] = np.where(has_review, az_review, az_biasa)
    elif 'Azimuth Review' in df_sumber.columns:
        az_review = pd.to_numeric(df_sumber['Azimuth Review'], errors='coerce')
        az_biasa = pd.to_numeric(df_sumber['Azimuth'], errors='coerce')
        
        # Cek per site, apakah site tersebut memiliki setidaknya satu nilai Azimuth Review yang valid
        has_review = az_review.groupby(df_sumber['Site ID Surge']).transform(lambda x: x.notna().any())
        
        # Jika site punya review, pakai az_review (walaupun ada NaN, biar sektor berkurang).
        # Jika tidak punya review sama sekali, pakai az_biasa.
        df_target['Azimuth'] = np.where(has_review, az_review, az_biasa)
    else:
        df_target['Azimuth'] = pd.to_numeric(df_sumber['Azimuth'], errors='coerce')

    kondisi_terbalik = (df_target['Longitude'].abs() < 20) & (df_target['Latitude'].abs() > 80)
    temp_lon = df_target.loc[kondisi_terbalik, 'Longitude']
    df_target.loc[kondisi_terbalik, 'Longitude'] = df_target.loc[kondisi_terbalik, 'Latitude']
    df_target.loc[kondisi_terbalik, 'Latitude'] = temp_lon

    df_target['Longitude'] = df_target.groupby('Site ID Surge')['Longitude'].transform(lambda x: x.ffill().bfill())
    df_target['Latitude'] = df_target.groupby('Site ID Surge')['Latitude'].transform(lambda x: x.ffill().bfill())

    df_target['Ant Height'] = 20
    df_target['H Beamwidth'] = 120
    df_target['Power'] = 46
    df_target['A Gain'] = 15
    df_target['Freq'] = 1400
    df_target['Band'] = 'n50'

    df_target = df_target.dropna(subset=['Site ID Surge', 'Longitude', 'Latitude', 'Azimuth'])
    for col in ['Ant Height', 'H Beamwidth', 'Power', 'A Gain', 'Freq']:
        df_target[col] = df_target[col].astype(int)

    return df_target

transformer_to_utm = Transformer.from_crs("EPSG:4326", "EPSG:32749", always_xy=True)
transformer_to_wgs = Transformer.from_crs("EPSG:32749", "EPSG:4326", always_xy=True)

def create_sector(lon, lat, azimuth, beamwidth, radius):
    x, y = transformer_to_utm.transform(lon, lat)
    beam_scale = 0.67
    bw_scaled = beamwidth * beam_scale
    start_angle = azimuth - bw_scaled / 2
    end_angle = azimuth + bw_scaled / 2

    pts = [(x, y)]
    for angle in np.linspace(start_angle, end_angle, 180):
        rad = math.radians(angle)
        px = x + radius * math.sin(rad)
        py = y + radius * math.cos(rad)
        pts.append((px, py))

    pts.append((x, y))
    pts_latlon = [transformer_to_wgs.transform(px, py) for px, py in pts]
    return Polygon(pts_latlon), start_angle, end_angle

def parse_input_data(text_data):
    if not text_data.strip():
        return None, "No data provided", 400

    def parse_coordinate(coord_str):
        coord_str = str(coord_str).strip().upper().replace(',', '.')
        if not coord_str or coord_str in ['NA', 'N/A', '-']:
            return None
        multiplier = 1.0
        if coord_str.endswith('S') or coord_str.endswith('W'):
            multiplier = -1.0
            coord_str = coord_str[:-1].strip()
        elif coord_str.endswith('N') or coord_str.endswith('E'):
            coord_str = coord_str[:-1].strip()
        try:
            return float(coord_str) * multiplier
        except ValueError:
            return None

    reader = csv.reader(io.StringIO(text_data.strip()), delimiter='\t')
    rows = list(reader)

    if not rows:
        return None, "No data provided", 400

    data_start = -1
    lat_col = -1
    lon_col = -1
    
    for i, row in enumerate(rows):
        if len(row) < 3:
            continue
            
        found = False
        for j in range(len(row) - 1, 0, -1):
            lon_val = parse_coordinate(row[j])
            lat_val = parse_coordinate(row[j-1])
            if lon_val is not None and lat_val is not None:
                if -180 <= lon_val <= 180 and -90 <= lat_val <= 90:
                    lat_col = j - 1
                    lon_col = j
                    found = True
                    break
                
        if found:
            data_start = i
            break
            
    if data_start == -1:
        return None, "Error: Could not detect Latitude/Longitude in the data. Make sure coordinates are present and valid.", 400

    num_cols = len(rows[data_start])
    header_row = rows[data_start - 1] if data_start > 0 else []
    
    headers = []
    if len(header_row) >= num_cols:
        headers = header_row[-num_cols:]
    else:
        pad_len = num_cols - len(header_row)
        headers = [f"Column {i+1}" for i in range(pad_len)] + header_row
        
    headers = [str(h).strip() for h in headers]
    if headers[0].startswith("Column") and "scenario" in rows[data_start][0].lower():
        headers[0] = "Scenario"

    last_values = {}
    points = []

    for row_idx, row in enumerate(rows[data_start:], start=1):
        if not row:
            continue
            
        while len(row) < num_cols:
            row.append('')

        row_data = {}
        for i, h in enumerate(headers):
            val = str(row[i]).strip()
            
            if not val and i < 3:
                val = last_values.get(i, '')
            else:
                last_values[i] = val
                
            row_data[h] = val

        lat_str = str(row[lat_col]).strip()
        lon_str = str(row[lon_col]).strip()

        lat = parse_coordinate(lat_str)
        lon = parse_coordinate(lon_str)

        if lat is None or lon is None:
            continue

        desc_html = '<table border="1" style="border-collapse: collapse;">'
        for k, v in row_data.items():
            desc_html += f'<tr><th style="padding: 5px; text-align: left;">{k}</th><td style="padding: 5px;">{v}</td></tr>'
        desc_html += '</table>'

        scenario = row_data.get(headers[0], '').strip()
        sector_val = ""
        for i, h in enumerate(headers):
            if 'sector' in h.lower():
                sector_val = row_data.get(h, '').strip()
                break
        
        if not sector_val and num_cols > 3:
            sector_val = row_data.get(headers[3], '').strip()

        name_parts = []
        if scenario: name_parts.append(scenario)
        if sector_val: name_parts.append(f"Sector {sector_val}")
            
        name = " ".join(name_parts) if name_parts else f"Point {row_idx}"
            
        points.append({
            'lat': lat,
            'lon': lon,
            'name': name,
            'desc_html': desc_html,
            'row_data': row_data
        })
        
    return points, None, 200

# ==============================
# HEADER & TOP MENU
# ==============================
st.markdown('<div class="glass-card" style="text-align: center;">', unsafe_allow_html=True)

if 'active_menu' not in st.session_state:
    st.session_state.active_menu = "📡 SSV Spot Generator"

menu_col1, menu_col2, menu_col3 = st.columns(3)
with menu_col1:
    btn_type1 = "primary" if st.session_state.active_menu == "📡 SSV Spot Generator" else "secondary"
    if st.button("📡 SSV Spot Generator", use_container_width=True, type=btn_type1):
        st.session_state.active_menu = "📡 SSV Spot Generator"
        st.rerun()

with menu_col2:
    btn_type2 = "primary" if st.session_state.active_menu == "📑 KMZ for ATP" else "secondary"
    if st.button("📑 KMZ for ATP", use_container_width=True, type=btn_type2):
        st.session_state.active_menu = "📑 KMZ for ATP"
        st.rerun()

with menu_col3:
    btn_type3 = "primary" if st.session_state.active_menu == "🎯 SSV Spot Checker" else "secondary"
    if st.button("🎯 SSV Spot Checker", use_container_width=True, type=btn_type3):
        st.session_state.active_menu = "🎯 SSV Spot Checker"
        st.rerun()

menu = st.session_state.active_menu

if menu == "📡 SSV Spot Generator":
    st.markdown("<h1>SSV Spot Generator</h1>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Render file KMZ Sektoral secara instan dan dinamis.</div>", unsafe_allow_html=True)
elif menu == "📑 KMZ for ATP":
    st.markdown("<h1>KMZ for ATP</h1>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Render file KMZ untuk kebutuhan ATP tanpa Spot SSV.</div>", unsafe_allow_html=True)
else:
    st.markdown("<h1>SSV Spot Checker</h1>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Validasi titik tes lapangan dengan koordinat sektor aktual.</div>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

with st.spinner('Mempersiapkan data...'):
    try:
        df_bersih = load_and_clean_data(SHEET_URL)
    except Exception as e:
        st.error(f"Gagal menarik data: {e}")
        st.stop()

# ==============================
# TOOL KONTROL (CENTERED)
# ==============================
points = []

if menu == "🎯 SSV Spot Checker":
    with st.expander("💡 Cara Penggunaan (How it works)", expanded=False):
        st.markdown("""
        <style>
        .instructions-premium {
            background: rgba(30, 41, 59, 0.4);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 20px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            margin-top: 5px;
        }
        .premium-table-wrapper {
            overflow-x: auto;
            margin: 15px 0;
            border-radius: 12px;
            border: 1px dashed #a78bfa;
            padding: 2px;
        }
        .premium-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85rem;
            background-color: rgba(15, 23, 42, 0.6);
            color: #e2e8f0;
        }
        .premium-table th {
            background-color: rgba(124, 58, 237, 0.2);
            color: #c4b5fd;
            padding: 10px;
            border: 1px solid rgba(255,255,255,0.05);
            text-align: center;
        }
        .premium-table td {
            padding: 8px;
            border: 1px solid rgba(255,255,255,0.05);
            text-align: center;
        }
        .premium-table td:nth-child(1), .premium-table td:nth-child(2), .premium-table td:nth-child(3) {
            background-color: rgba(0,0,0,0.2);
        }
        .bullet-list li {
            color: #cbd5e1;
            margin-bottom: 8px;
        }
        .bullet-list strong {
            color: #a78bfa;
        }
        </style>
        <div class="instructions-premium">
            <p style="color: #cbd5e1; font-size: 1.05rem;"><strong>Just copy paste all!</strong> Contoh tabel dari Excel/Spreadsheet yang bisa langsung Anda copy:</p>
            <div class="premium-table-wrapper">
                <table class="premium-table">
                    <thead>
                        <tr>
                            <th colspan="8" style="background: linear-gradient(90deg, #7c3aed, #db2777); color: white; font-size: 1.1rem;">TEST INFORMATION</th>
                        </tr>
                        <tr>
                            <th>Scenario</th>
                            <th>Distance<br>to BTS (mtr)</th>
                            <th>Target<br>(Mbps)</th>
                            <th>Sector</th>
                            <th>Position</th>
                            <th>Category</th>
                            <th>Latitude</th>
                            <th>Longitude</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td rowspan="3" style="font-weight: bold;">Scenario 1</td>
                            <td rowspan="3" style="font-weight: bold;">50-150</td>
                            <td rowspan="3" style="font-weight: bold;">DL 315</td>
                            <td>1</td><td>Outdoor</td><td>high dense res.</td><td>-6,8622</td><td>109,1379</td>
                        </tr>
                        <tr><td>2</td><td>Outdoor</td><td>high dense res.</td><td>-6,8638</td><td>109,1375</td></tr>
                        <tr><td>3</td><td>Outdoor</td><td>high dense res.</td><td>-6,8626</td><td>109,1364</td></tr>
                        <tr>
                            <td rowspan="3" style="font-weight: bold;">Scenario 2</td>
                            <td rowspan="3" style="font-weight: bold;">250-350</td>
                            <td rowspan="3" style="font-weight: bold;">DL 150</td>
                            <td>1</td><td>Outdoor</td><td>high dense res.</td><td>-6,8609</td><td>109,1392</td>
                        </tr>
                        <tr><td>2</td><td>Outdoor</td><td>high dense res.</td><td>-6,8654</td><td>109,1379</td></tr>
                        <tr><td>3</td><td>Outdoor</td><td>high dense res.</td><td>-6,8621</td><td>109,1344</td></tr>
                        <tr>
                            <td rowspan="3" style="font-weight: bold;">Scenario 3</td>
                            <td rowspan="3" style="font-weight: bold;">400-500</td>
                            <td rowspan="3" style="font-weight: bold;">DL 50</td>
                            <td>1</td><td>Outdoor</td><td>high dense res.</td><td>-6,8597</td><td>109,1404</td>
                        </tr>
                        <tr><td>2</td><td>Outdoor</td><td>high dense res.</td><td>-6,8672</td><td>109,1384</td></tr>
                        <tr><td>3</td><td>Outdoor</td><td>high dense res.</td><td>-6,8616</td><td>109,1329</td></tr>
                    </tbody>
                </table>
            </div>
            <ul class="bullet-list">
                <li>Blok seluruh data di tabel Anda (seperti area dengan garis putus-putus ungu di atas).</li>
                <li>Tekan <strong>Ctrl+C</strong> (Copy) lalu <strong>Ctrl+V</strong> (Paste) ke kotak input di bawah.</li>
                <li>Klik tombol <strong>📍 Tampilkan Titik di Peta (Process Data)</strong> untuk merekam koordinat tes lapangan Anda.</li>
                <li>Cari dan pilih <strong>Site ID</strong> tujuan pada kotak pencarian di bawah untuk membuka Peta Interaktif.</li>
                <li>Klik <strong>🚀 Download File KMZ</strong> untuk mendapatkan file Super KMZ yang menggabungkan sektor dan titik tes Anda!</li>
                <li><em>(Catatan: Sistem kami otomatis mendeteksi sel yang di-merge dan membersihkan format titik/koma secara mandiri)</em></li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    with st.form("data_form", border=False):
        pasted_data = st.text_area("Paste your spreadsheet data here (Excel/Sheets):", height=150, placeholder="Scenario 1\t50-150\tDL 315\t1\tOutdoor\thigh dense residential\t-6.967333\t110.128127")
        submit_btn = st.form_submit_button("📍 Tampilkan Titik di Peta (Process Data)", use_container_width=True)

    if pasted_data.strip():
        res, err, _ = parse_input_data(pasted_data)
        if err:
            st.warning(err)
        elif res:
            points = res
            st.success(f"Berhasil membaca {len(points)} titik tes lapangan.")
    
    st.markdown("<br>", unsafe_allow_html=True)


st.markdown('<div class="glass-card">', unsafe_allow_html=True)
col1, col2 = st.columns([4, 1])
site_list = sorted(df_bersih['Site ID Surge'].unique().tolist())

with col1:
    selected_site = st.selectbox(
        "🔍 Cari Site ID:", 
        site_list, 
        index=None, 
        placeholder="Ketik Site ID di sini..."
    )
    
with col2:
    st.markdown("<br>", unsafe_allow_html=True) # Spacer agar sejajar dengan selectbox
    if st.button("🔄 Sync Data", use_container_width=True, help="Tarik data terbaru dari Google Sheets"):
        st.cache_data.clear()
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)



if selected_site:
    df_filtered = df_bersih[df_bersih['Site ID Surge'] == selected_site].reset_index(drop=True)
    site_name = df_filtered.iloc[0]['Site Name Surge']
    center_lon = float(df_filtered.iloc[0]['Longitude'])
    center_lat = float(df_filtered.iloc[0]['Latitude'])
    
    
    st.markdown(f"### 📍 {site_name} <span style='font-size: 0.8rem; background-color: #1a4d2e; color: #4ade80; padding: 4px 10px; border-radius: 12px; vertical-align: middle; margin-left: 10px;'>🟢 Sync: LLD Fiberhome</span>", unsafe_allow_html=True)
    
    azimuths_str = ", ".join(df_filtered['Azimuth'].astype(int).astype(str).tolist())
    maps_url = f"https://www.google.com/maps/dir/?api=1&destination={center_lat},{center_lon}"
    
    st.markdown(f"""
    <div style="font-size: 0.9rem; color: #a0aec0; margin-bottom: 15px;">
        Site ID: {selected_site} &nbsp;|&nbsp; Total Sektor: {len(df_filtered)} &nbsp;|&nbsp; Azimuth: {azimuths_str} &nbsp;|&nbsp; 
        <a href="{maps_url}" target="_blank" style="color: #00f2fe; text-decoration: none; font-weight: bold; background: rgba(0, 242, 254, 0.1); padding: 2px 6px; border-radius: 4px;">
            🧭 Rute ke Lokasi ({center_lat:.5f}, {center_lon:.5f})
        </a>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("<h3 style='margin-top: 0px; margin-bottom: 15px; color: #e2e8f0; font-weight: 600;'>🌍 Live Interactive Map Preview</h3>", unsafe_allow_html=True)
    
    # Map Preview dengan tema gelap (CartoDB dark_matter) agar seirama dengan Dark Mode
    m = folium.Map(location=[center_lat, center_lon], zoom_start=16, tiles='CartoDB dark_matter', control_scale=True)
    
    # Tambahkan Google Satellite Layer
    folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
        attr='Google',
        name='Google Satellite',
        overlay=False,
        control=True
    ).add_to(m)
    
    # Tambahkan Measure Control (Penggaris Pintar)
    m.add_child(MeasureControl(position='topleft', primary_length_unit='meters', secondary_length_unit='kilometers'))
    
    # Tambahkan Locate Control (GPS Nativ di dalam Map)
    LocateControl(
        position="topleft", 
        drawCircle=True,
        flyTo=True, 
        strings={"title": "📍 Klik untuk terbang ke Lokasi Saya", "popup": "Posisi Anda Sekarang!"}
    ).add_to(m)
    
    # Inject CSS untuk merubah tombol LocateControl menjadi lebar dan ada tulisannya
    locate_css = """
    <style>
    .leaflet-control-locate a {
        width: auto !important;
        padding: 0 8px !important;
        font-weight: bold !important;
        font-family: sans-serif !important;
        color: #2c3e50 !important;
        text-decoration: none !important;
        display: flex !important;
        align-items: center !important;
        gap: 5px !important;
    }
    .leaflet-control-locate a::after {
        content: 'Locate Me';
    }
    </style>
    """
    m.get_root().header.add_child(Element(locate_css))
    
    # Setup Feature Groups untuk Layer Control
    fg_rings = folium.FeatureGroup(name='Ring Radius', show=True)
    fg_sectors = folium.FeatureGroup(name='Sektor (Polygon)', show=True)
    fg_lines = folium.FeatureGroup(name='Garis Azimuth', show=True)
    fg_spots = folium.FeatureGroup(name='Titik Tes (Field)', show=True)
    
    folium.Marker([center_lat, center_lon], popup=site_name, tooltip="Pusat Site", icon=folium.Icon(color='lightgray', icon='info-sign')).add_to(m)
    
    # Tambahkan RING (100m, 300m, 500m) ke peta web
    for r in [100, 300, 500]:
        folium.Circle(
            location=[center_lat, center_lon],
            radius=r,
            color='white',
            weight=1,
            fill=False,
            tooltip=f"Ring {r}m"
        ).add_to(fg_rings)

    colors = ['#00ff00', '#ff0000', '#ffff00', '#0000ff', '#ff00ff']
    x0, y0 = transformer_to_utm.transform(center_lon, center_lat)

    for sec_idx, (_, row) in enumerate(df_filtered.iterrows(), start=1):
        lon = float(row['Longitude'])
        lat = float(row['Latitude'])
        az = float(row['Azimuth'])
        bw = float(row['H Beamwidth'])
        
        # Sector polygon
        sector, _, _ = create_sector(lon, lat, az, bw, 500) 
        coords = [(y, x) for x, y in sector.exterior.coords]
        
        pci_val = row.get('PCI', '-')
        cell_name = row.get('Cell Name', '-')
        
        tooltip_html = f"<div style='min-width:120px; font-family:sans-serif;'><b>Sektor {sec_idx}</b><br>Azimuth: {az}°<br>PCI: {pci_val}<br>Sector: {cell_name}</div>"
        
        color = colors[(sec_idx - 1) % len(colors)]
        folium.Polygon(
            locations=coords, color=color, fill=True, fill_opacity=0.2,
            weight=1, tooltip=tooltip_html
        ).add_to(fg_sectors)
        
        # Line dan Spot dari perhitungan KMZ, ditambahkan ke Folium
        rad = math.radians(az)
        px_line = x0 + 500 * math.sin(rad)
        py_line = y0 + 500 * math.cos(rad)
        lon_line_end, lat_line_end = transformer_to_wgs.transform(px_line, py_line)
        
        # Line dari site ke 500m
        folium.PolyLine(
            locations=[[lat, lon], [lat_line_end, lon_line_end]],
            color='white',
            weight=2,
            tooltip=f"Garis Azimuth Sektor {sec_idx}"
        ).add_to(fg_lines)
        
        if menu != "📑 KMZ for ATP":
            # Spots at 100m, 300m, 500m
            spot_counter = 1
            for dist in [100, 300, 500]:
                px_spot = x0 + dist * math.sin(rad)
                py_spot = y0 + dist * math.cos(rad)
                lon_spot, lat_spot = transformer_to_wgs.transform(px_spot, py_spot)
                
                icon_color = "blue" if spot_counter == 2 else "orange"
                folium.Marker(
                    location=[lat_spot, lon_spot],
                    tooltip=f"Sec {sec_idx} Spot {spot_counter} ({dist}m)",
                    icon=folium.Icon(color=icon_color, icon='info-sign')
                ).add_to(fg_lines)
                spot_counter += 1

    if points:
        for pt in points:
            folium.Marker(
                location=[pt['lat'], pt['lon']],
                popup=folium.Popup(pt['desc_html'], max_width=300),
                tooltip=pt['name'],
                icon=folium.Icon(color='red', icon='info-sign')
            ).add_to(fg_spots)

    # Tambahkan FeatureGroups ke Map
    fg_rings.add_to(m)
    fg_sectors.add_to(m)
    fg_lines.add_to(m)
    fg_spots.add_to(m)

    # Tambahkan LayerControl
    folium.LayerControl(position='topright').add_to(m)

    # Render Map di Streamlit
    st_folium(m, height=450, use_container_width=True, returned_objects=[])
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ==============================
    # MINI ANALYTICS & RADAR PLOT
    # ==============================
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("<h3 style='margin-top: 0px; margin-bottom: 15px; color: #e2e8f0; font-weight: 600;'>📊 Mini Analytics & Radar Azimuth</h3>", unsafe_allow_html=True)
    
    ana_col1, ana_col2 = st.columns([1, 1.5])
    
    with ana_col1:
        # Radar Chart for Azimuths
        df_radar = pd.DataFrame({
            'r': [1] * len(df_filtered),
            'theta': df_filtered['Azimuth'].astype(float),
            'Sektor': [f"Sec {i+1}" for i in range(len(df_filtered))]
        })
        fig = px.line_polar(df_radar, r='r', theta='theta', text='Sektor', line_close=True, range_r=[0, 1.5], template='plotly_dark')
        fig.update_traces(fill='toself', marker=dict(size=10))
        fig.update_layout(polar=dict(angularaxis=dict(direction='clockwise', rotation=90)), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=20, b=20, l=20, r=20), height=300)
        st.plotly_chart(fig, use_container_width=True)

    with ana_col2:
        st.markdown("<h4 style='color:#a78bfa;'>📍 Jarak Aktual Titik Tes (Haversine)</h4>", unsafe_allow_html=True)
        if points:
            dist_data = []
            for pt in points:
                actual_dist = geodesic((center_lat, center_lon), (pt['lat'], pt['lon'])).meters
                dist_data.append({
                    "Titik Tes": pt['name'],
                    "Jarak Aktual (m)": f"{actual_dist:.1f} m"
                })
            df_dist = pd.DataFrame(dist_data)
            st.dataframe(df_dist, use_container_width=True, hide_index=True)
        else:
            st.info("Belum ada data Titik Tes Lapangan yang dimasukkan.")
            
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Generate KMZ Data
    with st.status('⏳ Membangun File Super KMZ...', expanded=True) as status:
        st.write("🔍 Mempersiapkan metadata Site...")
        kml = simplekml.Kml()
        site_id = selected_site
        folder_site = kml.newfolder(name=f"{site_id} - {site_name}")
        folder_site.visibility = 1

        p_site = folder_site.newpoint(name=f"{site_id} - {site_name}")
        p_site.coords = [(center_lon, center_lat)]
        p_site.style.iconstyle.color = simplekml.Color.white
        p_site.visibility = 1

        st.write("⭕ Membuat poligon Radius (100m, 300m, 500m)...")

        st.write("⭕ Membuat poligon Ring Radius (100m, 300m, 500m)...")
        folder_ring = folder_site.newfolder(name="RING")
        folder_ring.visibility = 1

        for r in [100, 300, 500]:
            pol_ring = folder_ring.newpolygon(name=f"RING_{r}m")
            pol_ring.visibility = 1
            pts = []
            for deg in np.linspace(0, 360, 360):
                rad = math.radians(deg)
                px = x0 + r * math.sin(rad)
                py = y0 + r * math.cos(rad)
                pts.append(transformer_to_wgs.transform(px, py))
            pol_ring.outerboundaryis = pts
            pol_ring.style.linestyle.color = simplekml.Color.white
            pol_ring.style.linestyle.width = 3
            pol_ring.style.polystyle.fill = 0

        folder_az = folder_site.newfolder(name="AZIMUTH")
        folder_az.visibility = 1
        if menu != "📑 KMZ for ATP":
            folder_spot = folder_site.newfolder(name="SPOT SSV")
        st.write("🛰️ Membangun poligon Sektor dan Spot Area...")
        colors = ['ff00ff00', 'ff0000ff', 'ff00ffff', 'ffff0000', 'ffff00ff']
        for sec_idx, (_, row) in enumerate(df_filtered.iterrows(), start=1):
            lon = float(row['Longitude'])
            lat = float(row['Latitude'])
            az = float(row['Azimuth'])
            bw = float(row['H Beamwidth'])

            sector, _, _ = create_sector(lon, lat, az, bw, 500)
            pol = folder_az.newpolygon(name=f"Sec {sec_idx} Azimuth {int(az)}")
            pol.outerboundaryis = [(x, y) for x, y in sector.exterior.coords]
            pol.visibility = 1

            pol.description = "<br>".join([
                f"Site ID : {row['Site ID Surge']}", f"Site Name : {row['Site Name Surge']}",
                f"Longitude : {row['Longitude']}", f"Latitude : {row['Latitude']}",
                f"Azimuth : {row['Azimuth']}", f"Antenna Height : {row['Ant Height']}",
                f"Beamwidth : {row['H Beamwidth']}", f"Power : {row['Power']}",
                f"Antenna Gain : {row['A Gain']}", f"Frequency : {row['Freq']}", f"Band : {row['Band']}"
            ])

            color = simplekml.Color.green if sec_idx == 1 else (simplekml.Color.red if sec_idx == 2 else simplekml.Color.yellow)
            pol.style.polystyle.color = simplekml.Color.changealphaint(120, color)

            rad = math.radians(az)
            px_line = x0 + 500 * math.sin(rad)
            py_line = y0 + 500 * math.cos(rad)

            line = folder_az.newlinestring(name=f"LINE_{int(az)}")
            line.coords = [(lon, lat), transformer_to_wgs.transform(px_line, py_line)]
            line.style.linestyle.color = simplekml.Color.white
            line.style.linestyle.width = 2
            line.visibility = 1

            if menu != "📑 KMZ for ATP":
                folder_sec = folder_spot.newfolder(name=f"Sec {sec_idx}")
                folder_sec.visibility = 1
                spot_counter = 1

                for dist in [100, 300, 500]:
                    px_spot = x0 + dist * math.sin(rad)
                    py_spot = y0 + dist * math.cos(rad)
                    lon2, lat2 = transformer_to_wgs.transform(px_spot, py_spot)

                    pnt = folder_sec.newpoint(name=f"Sec {sec_idx} spot {spot_counter}")
                    pnt.coords = [(lon2, lat2)]
                    pnt.style.iconstyle.icon.href = "http://maps.google.com/mapfiles/kml/pushpin/blue-pushpin.png" if spot_counter == 2 else "http://maps.google.com/mapfiles/kml/pushpin/ylw-pushpin.png"
                    pnt.visibility = 1
                    spot_counter += 1

        if points:
            st.write("🎯 Menambahkan Field Test Points ke dalam KMZ...")
            folder_points = folder_site.newfolder(name="TITIK TES LAPANGAN")
            folder_points.visibility = 1
            for i, pt in enumerate(points, 1):
                p_spot = folder_points.newpoint(name=pt['name'])
                p_spot.coords = [(pt['lon'], pt['lat'])]
                p_spot.style.iconstyle.color = simplekml.Color.red
                p_spot.visibility = 1
                p_spot.description = pt['desc_html']

        if menu == "📑 KMZ for ATP":
            kmz_name = f"ATP_{site_id}_{datetime.now().strftime('%d%b%Y')}.kmz"
        else:
            kmz_name = f"SSV_{site_id}_{datetime.now().strftime('%d%b%Y')}.kmz"
        
        status.update(label="✅ Super KMZ Berhasil Dibuat!", state="complete", expanded=False)
        
        kml.save("temp.kml")
        import io
        kmz_io = io.BytesIO()
        with zipfile.ZipFile(kmz_io, 'w', zipfile.ZIP_DEFLATED) as z:
            z.write("temp.kml", arcname="doc.kml")
        
        kmz_data = kmz_io.getvalue()
        
        if os.path.exists("temp.kml"):
            os.remove("temp.kml")

    def celebration():
        st.balloons()
        
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        st.download_button(
            label="🚀 Download File KMZ",
            data=kmz_data,
            file_name=kmz_name,
            mime="application/vnd.google-earth.kmz",
            use_container_width=True,
            type="primary",
            on_click=celebration
        )
    
    with col_btn2:
        pdf_data = generate_pdf(site_id, site_name, df_filtered, dist_data if 'dist_data' in locals() else [])
        st.download_button(
            label="📑 Download PDF Report",
            data=bytes(pdf_data),
            file_name=f"SSV_Report_{site_id}_{datetime.now().strftime('%d%b%Y')}.pdf",
            mime="application/pdf",
            use_container_width=True,
            type="primary",
            on_click=celebration
        )
                
    st.markdown('</div>', unsafe_allow_html=True)

else:
    st.markdown("""
    <div style="text-align: center; color: #8b949e; margin-top: 50px;">
        <h1 style="font-size: 4rem; opacity: 0.2; background: none; -webkit-text-fill-color: #8b949e;">📡</h1>
        <p>Gunakan kotak pencarian di atas untuk memulai.</p>
    </div>
    """, unsafe_allow_html=True)
