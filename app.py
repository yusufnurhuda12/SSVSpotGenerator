# [UI-ONLY] SSV Tool - Fiberhome RF Console v2.7 (Playful Neo-Brutalism Saweria Style)
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
import base64
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
from tilting_manager import (
    fetch_gdrive_tilting_files,
    find_tilting_photos_for_site,
    download_image_bytes,
    create_tilting_zip,
    DRIVE_FOLDER_URL,
    FOLDER_ID
)

# ==============================
# [UI-ONLY] KONFIGURASI WEB & MASKOT MENARA
# ==============================
MASCOT_PATH = os.path.join(os.path.dirname(__file__), "assets", "mascot_menara.svg")
mascot_icon = MASCOT_PATH if os.path.exists(MASCOT_PATH) else None

st.set_page_config(
    page_title="SSV Tool",
    page_icon=mascot_icon,
    layout="wide",
    initial_sidebar_state="collapsed"
)

MASCOT_B64 = ""
if os.path.exists(MASCOT_PATH):
    try:
        with open(MASCOT_PATH, "rb") as f_m:
            MASCOT_B64 = base64.b64encode(f_m.read()).decode("utf-8")
    except Exception:
        MASCOT_B64 = ""

# ==============================
# [UI-ONLY] SAWERIA-INSPIRED NEO-BRUTALISM CSS (ZERO EMOJIS, HIGH CONTRAST)
# ==============================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800;900&family=Plus+Jakarta+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500;600;700&family=Comfortaa:wght@700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
    color: #1A1A1A;
    background-color: #F8F9F8 !important;
}

.stApp {
    background-color: #F8F9F8 !important;
}

.block-container {
    max-width: 1200px !important;
    padding-top: 56px !important;
    padding-bottom: 60px !important;
    padding-left: 20px !important;
    padding-right: 20px !important;
}

header[data-testid="stHeader"] {
    display: none !important;
}

/* Edge-to-Edge Top Amber Strip Banner */
.top-full-banner {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    width: 100vw;
    background: #FFAE2B;
    border-bottom: 2.5px solid #1A1A1A;
    padding: 7px 0;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.76rem;
    font-weight: 700;
    color: #1A1A1A;
    z-index: 999999;
    box-shadow: 0 2px 0px rgba(0,0,0,0.1);
    display: flex;
    justify-content: center;
}

/* Centered Hero Header with Floating Mascot */
.hero-header-box {
    text-align: center;
    padding: 24px 16px 14px 16px;
    margin-bottom: 8px;
}
.hero-mascot-container {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-bottom: 10px;
}
.hero-mascot-img {
    width: 165px;
    max-width: 38vw;
    height: auto;
    display: block;
    filter: drop-shadow(4px 4px 0px #1A1A1A);
    animation: mascotFloat 3.5s ease-in-out infinite;
}
@keyframes mascotFloat {
    0% { transform: translateY(0px); }
    50% { transform: translateY(-8px); }
    100% { transform: translateY(0px); }
}
@media (prefers-reduced-motion: reduce) {
    .hero-mascot-img {
        animation: none !important;
    }
}
.hero-title {
    font-family: 'Outfit', sans-serif;
    font-size: clamp(2rem, 5vw, 2.7rem);
    font-weight: 900;
    letter-spacing: -0.03em;
    color: #1A1A1A;
    margin: 0 0 4px 0;
    text-transform: uppercase;
}
.hero-subtitle {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.82rem;
    font-weight: 600;
    color: #4A4A4A;
    margin: 0;
    letter-spacing: 0.04em;
}

/* Streamlit Native Container Borders styled as Neo-Brutalist Cards */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #FFFFFF !important;
    border: 2px solid #1A1A1A !important;
    border-radius: 8px !important;
    box-shadow: 5px 5px 0px #1A1A1A !important;
    padding: 24px 22px 20px 22px !important;
    margin-bottom: 20px !important;
    position: relative !important;
}

/* Attached Card Tab (Anchored firmly inside the container) */
.card-attached-tab {
    position: absolute !important;
    top: -14px !important;
    right: 20px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    text-transform: lowercase !important;
    padding: 3px 12px !important;
    border: 1.5px solid #1A1A1A !important;
    border-radius: 4px !important;
    box-shadow: 2.5px 2.5px 0px #1A1A1A !important;
    z-index: 10 !important;
    letter-spacing: 0.02em !important;
}
.card-attached-tab.amber { background: #FFAE2B; color: #1A1A1A; }
.card-attached-tab.toska { background: #8DD3DB; color: #1A1A1A; }
.card-attached-tab.pink { background: #FFBCC4; color: #1A1A1A; }
.card-attached-tab.mint { background: #A9D6A0; color: #1A1A1A; }
.card-attached-tab.lavender { background: #D6C7FF; color: #1A1A1A; }

.subtitle {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.85rem;
    color: #4A4A4A;
    font-weight: 500;
    margin-top: 4px;
}

/* Badges */
.badge-pill, .live-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px;
    border-radius: 20px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    font-weight: 700;
    border: 1.5px solid #1A1A1A;
    box-shadow: 2px 2px 0px #1A1A1A;
    background: #A9D6A0;
    color: #1A1A1A;
}
.badge-pill-amber { background: #FFAE2B; color: #1A1A1A; }
.badge-pill-mint { background: #A9D6A0; color: #1A1A1A; }
.badge-pill-toska { background: #8DD3DB; color: #1A1A1A; }
.badge-pill-pink { background: #FFBCC4; color: #1A1A1A; }
.badge-pill-lavender { background: #D6C7FF; color: #1A1A1A; }
.badge-pill-slate { background: #E2E8F0; color: #1A1A1A; }

.pulse-dot {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background-color: #10b981;
    animation: livePulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    flex-shrink: 0;
}
@keyframes livePulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.4; transform: scale(0.85); }
}

/* Tab Navigation Buttons */
div[data-testid="column"] div[data-testid="stButton"] button {
    width: 100% !important;
    height: 48px !important;
    font-family: 'Comfortaa', 'Outfit', sans-serif !important;
    font-size: 0.88rem !important;
    font-weight: 800 !important;
    border: 2px solid #1A1A1A !important;
    border-radius: 6px !important;
    transition: all 0.1s ease !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 8px !important;
}
div[data-testid="column"] div[data-testid="stButton"] button[kind="secondary"] {
    background: #FFFFFF !important;
    color: #1A1A1A !important;
    box-shadow: 4px 4px 0px #1A1A1A !important;
}
div[data-testid="column"] div[data-testid="stButton"] button[kind="secondary"]:hover {
    transform: translate(2px, 2px) !important;
    box-shadow: 2px 2px 0px #1A1A1A !important;
}
div[data-testid="column"]:nth-of-type(1) div[data-testid="stButton"] button[kind="primary"] {
    background: #FFAE2B !important;
    color: #1A1A1A !important;
    box-shadow: 0px 0px 0px #1A1A1A !important;
    transform: translate(3px, 3px) !important;
}
div[data-testid="column"]:nth-of-type(2) div[data-testid="stButton"] button[kind="primary"] {
    background: #8DD3DB !important;
    color: #1A1A1A !important;
    box-shadow: 0px 0px 0px #1A1A1A !important;
    transform: translate(3px, 3px) !important;
}
div[data-testid="column"]:nth-of-type(3) div[data-testid="stButton"] button[kind="primary"] {
    background: #FFBCC4 !important;
    color: #1A1A1A !important;
    box-shadow: 0px 0px 0px #1A1A1A !important;
    transform: translate(3px, 3px) !important;
}
div[data-testid="column"]:nth-of-type(4) div[data-testid="stButton"] button[kind="primary"] {
    background: #D6C7FF !important;
    color: #1A1A1A !important;
    box-shadow: 0px 0px 0px #1A1A1A !important;
    transform: translate(3px, 3px) !important;
}

/* Material Symbols in buttons and text */
span[data-testid="stIconMaterial"] {
    color: #1A1A1A !important;
    font-size: 1.15rem !important;
    vertical-align: middle !important;
}

/* Sync Data Button Styling (Lavender with 5px hard shadow) */
div[data-testid="column"]:nth-of-type(2) div[data-testid="stButton"] button {
    background: #D4C8E8 !important;
    color: #1A1A1A !important;
    border: 2px solid #1A1A1A !important;
    border-radius: 6px !important;
    box-shadow: 5px 5px 0px #1A1A1A !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-weight: 800 !important;
    font-size: 0.88rem !important;
    height: 44px !important;
}
div[data-testid="column"]:nth-of-type(2) div[data-testid="stButton"] button:hover {
    transform: translate(2px, 2px) !important;
    box-shadow: 3px 3px 0px #1A1A1A !important;
}

/* Selectbox Dropdown Styling (White, 2px border, 4px shadow, focus amber) */
div[data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    border: 2px solid #1A1A1A !important;
    border-radius: 6px !important;
    box-shadow: 4px 4px 0px #1A1A1A !important;
    color: #1A1A1A !important;
    transition: all 0.15s ease !important;
}
div[data-baseweb="select"]:focus-within > div {
    border-color: #1A1A1A !important;
    box-shadow: 4px 4px 0px #FFAE2B !important;
}
div[data-baseweb="select"] * {
    color: #1A1A1A !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-weight: 600 !important;
}

/* Site Bento Grid Cards */
.site-bento-grid {
    display: grid;
    grid-template-columns: 1fr 1fr 1.1fr 1.6fr;
    gap: 12px;
    margin-top: 14px;
}
@media (max-width: 820px) {
    .site-bento-grid {
        grid-template-columns: 1fr 1fr;
    }
}
@media (max-width: 520px) {
    .site-bento-grid {
        grid-template-columns: 1fr;
    }
}
.bento-chip {
    border: 2px solid #1A1A1A;
    border-radius: 6px;
    padding: 10px 14px;
    box-shadow: 4px 4px 0px #1A1A1A;
    display: flex;
    flex-direction: column;
    justify-content: center;
    min-width: 0;
}
.bento-chip-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    font-weight: 700;
    color: #1A1A1A;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 3px;
}
.bento-chip-val {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1rem;
    font-weight: 800;
    color: #1A1A1A;
    overflow-wrap: anywhere;
    white-space: normal;
}
.bento-chip-val-coord {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.82rem;
    font-weight: 700;
    color: #1A1A1A;
    overflow-wrap: anywhere;
    white-space: normal;
    line-height: 1.35;
}

/* Sector Legend Bar */
.legend-bar {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 10px;
    background: #FFFFFF;
    border: 1.5px solid #1A1A1A;
    border-radius: 6px;
    padding: 5px 12px;
    box-shadow: 3px 3px 0px #1A1A1A;
}
.legend-item {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.78rem;
    font-weight: 600;
    color: #1A1A1A;
}
.legend-dot {
    display: inline-block;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    border: 1px solid #1A1A1A;
    flex-shrink: 0;
}

/* Symmetrical Action Download Buttons (Amber KMZ & Toska PDF) */
div[data-testid="stDownloadButton"] button {
    min-height: 56px !important;
    height: 56px !important;
    border: 2.5px solid #1A1A1A !important;
    border-radius: 6px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 1rem !important;
    font-weight: 800 !important;
    letter-spacing: 0.02em !important;
    box-shadow: 5px 5px 0px #1A1A1A !important;
    transition: all 0.12s ease !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    cursor: pointer !important;
    gap: 8px !important;
}
div[data-testid="stDownloadButton"] button:hover {
    transform: translate(2px, 2px) !important;
    box-shadow: 3px 3px 0px #1A1A1A !important;
}
div[data-testid="stDownloadButton"] button:active {
    transform: translate(4px, 4px) !important;
    box-shadow: 0px 0px 0px #1A1A1A !important;
}
div[data-testid="column"]:nth-of-type(1) div[data-testid="stDownloadButton"] button {
    background: #FFAE2B !important; /* Amber for KMZ */
    color: #1A1A1A !important;
}
div[data-testid="column"]:nth-of-type(2) div[data-testid="stDownloadButton"] button {
    background: #8DD3DB !important; /* Toska for PDF */
    color: #1A1A1A !important;
}

/* Status Widget: Flat Mint Card with Dark Border & Hard Shadow */
div[data-testid="stStatusWidget"] {
    background: #E8F5E9 !important;
    border: 2px solid #1A1A1A !important;
    border-radius: 8px !important;
    box-shadow: 4px 4px 0px #1A1A1A !important;
    margin-bottom: 16px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    color: #1A1A1A !important;
}

/* Expander Neo-Brutalism */
div[data-testid="stExpander"] {
    background: #FFFFFF !important;
    border: 2px solid #1A1A1A !important;
    border-radius: 6px !important;
    box-shadow: 3px 3px 0px #1A1A1A !important;
    margin-bottom: 14px !important;
}
div[data-testid="stExpander"] summary {
    font-family: 'Comfortaa', cursive !important;
    font-weight: 700 !important;
    color: #1A1A1A !important;
}

/* Textarea Neo-Brutalism */
div[data-testid="stTextArea"] textarea {
    background-color: #FFFFFF !important;
    border: 2px solid #1A1A1A !important;
    border-radius: 6px !important;
    box-shadow: 4px 4px 0px #1A1A1A !important;
    font-family: 'IBM Plex Mono', monospace !important;
    color: #1A1A1A !important;
}
</style>
""", unsafe_allow_html=True)

# [UI-ONLY] Top Banner
st.markdown("""
<div class="top-full-banner">
    <div style="display: flex; justify-content: space-between; align-items: center; width: 100%; max-width: 1200px; padding: 0 16px;">
        <span style="display: flex; align-items: center; gap: 8px;">
            <span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: #1A1A1A;"></span>
            <span>CONNECT WITH LLD: GnB Online Jekri Daeng</span>
        </span>
        <span>SSV TOOL // #sudahpastibagus </span>
    </div>
</div>
""", unsafe_allow_html=True)

# [UI-ONLY] Centered Hero Header with Mascot
st.markdown(f"""
<div class="hero-header-box">
    <div class="hero-mascot-container">
        <img src="data:image/svg+xml;base64,{MASCOT_B64}" alt="Menara - Maskot SSV Tool" class="hero-mascot-img" />
    </div>
    <h1 class="hero-title">SSV TOOL</h1>
    <p class="hero-subtitle">Back To Nature</p>
</div>
""", unsafe_allow_html=True)

# ==============================
# URL CSV & DATA CLEANSING (EXACT CUSTOMER TEMPLATE)
# ==============================
SHEET_URL = "https://docs.google.com/spreadsheets/d/1Yscupy_kQJzFBLOv_2lS0u2J-fKi5XqFoCyjRFXDlLA/export?format=csv&gid=118124849"

@st.cache_data(ttl=600)
def load_and_clean_data(url):
    try:
        df_sumber = pd.read_csv(url)
    except Exception:
        fallback_url = "https://docs.google.com/spreadsheets/d/1Yscupy_kQJzFBLOv_2lS0u2J-fKi5XqFoCyjRFXDlLA/gviz/tq?tqx=out:csv&gid=118124849"
        df_sumber = pd.read_csv(fallback_url)

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
        has_review = az_review.groupby(df_sumber['Site ID Surge']).transform(lambda x: x.notna().any())
        df_target['Azimuth'] = np.where(has_review, az_review, az_biasa)
    elif 'Azimuth Review' in df_sumber.columns:
        az_review = pd.to_numeric(df_sumber['Azimuth Review'], errors='coerce')
        az_biasa = pd.to_numeric(df_sumber['Azimuth'], errors='coerce')
        has_review = az_review.groupby(df_sumber['Site ID Surge']).transform(lambda x: x.notna().any())
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

# ==============================
# PROJEKSI & GEOMETRI SEKTOR (EXACT EPSG:32749 & BEAM SCALE 0.67)
# ==============================
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

# ==============================
# FIELD TEST PARSER (EXACT CUSTOMER TEMPLATE)
# ==============================
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

        sec_num = ''.join(filter(str.isdigit, sector_val)) if sector_val else ""
        scen_num = ''.join(filter(str.isdigit, scenario)) if scenario else ""

        if sec_num and scen_num:
            name = f"Sec{sec_num}_Scen{scen_num}"
        elif sec_num:
            name = f"Sec{sec_num}"
        elif scen_num:
            name = f"Scen{scen_num}"
        else:
            name_parts = []
            if sector_val: name_parts.append(f"Sec {sector_val}")
            if scenario: name_parts.append(scenario)
            name = "_".join(name_parts) if name_parts else f"Point_{row_idx}"
            
        points.append({
            'lat': lat,
            'lon': lon,
            'name': name,
            'desc_html': desc_html,
            'row_data': row_data
        })
        
    return points, None, 200

# ==============================
# [UI-ONLY] HEADER & TOP MENU NAVIGATION (4 SAWERIA TABS, ZERO EMOJIS)
# ==============================
if 'active_menu' not in st.session_state:
    st.session_state.active_menu = "SSV Spot Generator"
else:
    # Normalize legacy emoji session state
    cur_m = st.session_state.active_menu
    if "Spot Generator" in cur_m:
        st.session_state.active_menu = "SSV Spot Generator"
    elif "ATP" in cur_m:
        st.session_state.active_menu = "KMZ for ATP V2"
    elif "Checker" in cur_m:
        st.session_state.active_menu = "SSV Spot Checker"
    elif "Tilting" in cur_m:
        st.session_state.active_menu = "Tilting Recommendation"

menu_col1, menu_col2, menu_col3, menu_col4 = st.columns(4)
with menu_col1:
    btn_type1 = "primary" if st.session_state.active_menu == "SSV Spot Generator" else "secondary"
    if st.button("SSV Spot Generator", use_container_width=True, type=btn_type1, icon=":material/cell_tower:"):
        st.session_state.active_menu = "SSV Spot Generator"
        st.rerun()

with menu_col2:
    btn_type2 = "primary" if st.session_state.active_menu in ["KMZ for ATP V2", "KMZ for ATP"] else "secondary"
    if st.button("KMZ for ATP V2", use_container_width=True, type=btn_type2, icon=":material/description:"):
        st.session_state.active_menu = "KMZ for ATP V2"
        st.rerun()

with menu_col3:
    btn_type3 = "primary" if st.session_state.active_menu == "SSV Spot Checker" else "secondary"
    if st.button("SSV Spot Checker", use_container_width=True, type=btn_type3, icon=":material/my_location:"):
        st.session_state.active_menu = "SSV Spot Checker"
        st.rerun()

with menu_col4:
    btn_type4 = "primary" if st.session_state.active_menu == "Tilting Recommendation" else "secondary"
    if st.button("Tilting Recommendation", use_container_width=True, type=btn_type4, icon=":material/architecture:"):
        st.session_state.active_menu = "Tilting Recommendation"
        st.rerun()

menu = st.session_state.active_menu

# [UI-ONLY] Subheader Module Banner (Fixed: wrapped in st.container, no empty cards)
with st.container(border=True):
    if menu == "SSV Spot Generator":
        st.markdown("""
        <div style="text-align: center; padding: 4px 0;">
            <h1 style="font-family: 'Comfortaa', cursive; font-size: 1.35rem; font-weight: 800; margin: 0; color: #1A1A1A;">SSV Spot Generator</h1>
            <div class="subtitle">Buat file KMZ sektoral lengkap dengan garis azimuth dan panduan titik uji secara otomatis.</div>
        </div>
        """, unsafe_allow_html=True)
    elif menu in ["KMZ for ATP V2", "KMZ for ATP"]:
        st.markdown("""
        <div style="text-align: center; padding: 4px 0;">
            <h1 style="font-family: 'Comfortaa', cursive; font-size: 1.35rem; font-weight: 800; margin: 0; color: #1A1A1A;">KMZ for ATP V2</h1>
            <div class="subtitle">Siapkan file KMZ siap pakai untuk dokumen ATP, lengkap dengan sektor 100m dan titik skenario.</div>
        </div>
        """, unsafe_allow_html=True)
    elif menu == "KMZ for ATP V1":
        st.markdown("""
        <div style="text-align: center; padding: 4px 0;">
            <h1 style="font-family: 'Comfortaa', cursive; font-size: 1.35rem; font-weight: 800; margin: 0; color: #1A1A1A;">KMZ for ATP V1</h1>
            <div class="subtitle">Buat file KMZ berformat ringkas khusus untuk kebutuhan pelaporan ATP awal.</div>
        </div>
        """, unsafe_allow_html=True)
    elif menu == "SSV Spot Checker":
        st.markdown("""
        <div style="text-align: center; padding: 4px 0;">
            <h1 style="font-family: 'Comfortaa', cursive; font-size: 1.35rem; font-weight: 800; margin: 0; color: #1A1A1A;">SSV Spot Checker</h1>
            <div class="subtitle">Cocokkan koordinat hasil uji lapangan Anda langsung dengan posisi sektor aktual di peta.</div>
        </div>
        """, unsafe_allow_html=True)
    elif menu == "Tilting Recommendation":
        st.markdown("""
        <div style="text-align: center; padding: 4px 0;">
            <h1 style="font-family: 'Comfortaa', cursive; font-size: 1.35rem; font-weight: 800; margin: 0; color: #1A1A1A;">Tilting Recommendation</h1>
            <div class="subtitle">Download dan pratinjau foto rekomendasi tilting antena berdasarkan Site ID langsung dari Google Drive.</div>
        </div>
        """, unsafe_allow_html=True)

with st.spinner('Mempersiapkan data...'):
    try:
        df_bersih = load_and_clean_data(SHEET_URL)
    except Exception as e:
        st.error(f"Gagal menarik data: {e}", icon=":material/error:")
        st.stop()

# ==============================
# MODUL: TILTING RECOMMENDATION
# ==============================
if menu == "Tilting Recommendation":
    with st.container(border=True):
        st.markdown('<div class="card-attached-tab mint">pencarian rekomendasi tilting</div>', unsafe_allow_html=True)
        
        with st.spinner('Mengambil data foto rekomendasi tilting dari Google Drive...'):
            try:
                tilting_files = fetch_gdrive_tilting_files()
            except Exception:
                tilting_files = {}
        
        total_photos = len(tilting_files)
        
        # [UI-ONLY] Status Banner
        st.markdown(f'''
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; margin-bottom: 18px; padding-bottom: 16px; border-bottom: 1.5px solid #1A1A1A;">
            <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
                <span class="live-badge"><span class="pulse-dot"></span> Google Drive Terhubung</span>
                <span class="badge-pill badge-pill-lavender">
                    {total_photos} Foto Tilting Tersedia
                </span>
            </div>
            <div>
                <a href="{DRIVE_FOLDER_URL}" target="_blank" style="display: inline-flex; align-items: center; gap: 6px; color: #1A1A1A; text-decoration: none; font-weight: 700; font-size: 0.85rem; font-family: 'IBM Plex Mono', monospace; background: #8DD3DB; border: 1.5px solid #1A1A1A; padding: 6px 14px; border-radius: 6px; box-shadow: 3px 3px 0px #1A1A1A;">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z"/></svg> Buka Folder Google Drive
                </a>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        col_search, col_sync = st.columns([4, 1])
        
        drive_site_ids = sorted(list(set([info['site_id'] for info in tilting_files.values()])))
        sheet_site_ids = sorted(df_bersih['Site ID Surge'].unique().tolist())
        
        all_site_options = []
        for s_id in drive_site_ids:
            all_site_options.append(f"{s_id} (Foto Tersedia)")
        for s_id in sheet_site_ids:
            if s_id not in drive_site_ids:
                all_site_options.append(s_id)
                
        with col_search:
            selected_option = st.selectbox(
                "Cari / Pilih Site ID untuk Unduh Foto Tilting:",
                options=all_site_options,
                index=None,
                placeholder="Ketik Site ID (contoh: 32CBN_0224, 33BTG_0002)..."
            )
            
        with col_sync:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("Sync Drive", use_container_width=True, icon=":material/sync:", help="Tarik ulang daftar foto terbaru dari Google Drive"):
                st.cache_data.clear()
                st.rerun()
        
    if selected_option:
        clean_selected = selected_option.replace(" (Foto Tersedia)", "").strip()
        matched_photos = find_tilting_photos_for_site(clean_selected, tilting_files)
        df_site_info = df_bersih[df_bersih['Site ID Surge'].str.upper() == clean_selected.upper()]
        
        with st.container(border=True):
            st.markdown('<div class="card-attached-tab lavender">detail rekomendasi tilting</div>', unsafe_allow_html=True)
            
            if matched_photos:
                st.markdown(f'''
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; margin-bottom: 16px;">
                    <div>
                        <h2 style="margin: 0; font-size: 1.3rem; font-weight: 800; color: #1A1A1A; font-family: 'Comfortaa', cursive;">SITE ID: {clean_selected}</h2>
                        <p style="color: #4A4A4A; font-size: 0.85rem; margin: 4px 0 0 0; font-family: 'IBM Plex Mono', monospace;">
                            Ditemukan <b style="color: #1A1A1A;">{len(matched_photos)} file rekomendasi tilting</b> untuk site ini.
                        </p>
                    </div>
                    <span class="badge-pill badge-pill-mint"><span class="pulse-dot"></span> FOTO SIAP UNDUH</span>
                </div>
                ''', unsafe_allow_html=True)
                
                if not df_site_info.empty:
                    r_first = df_site_info.iloc[0]
                    az_str = ", ".join(df_site_info['Azimuth'].astype(int).astype(str).tolist())
                    st.markdown(f'''
                    <div style="background: #F1F5F3; border: 1.5px solid #1A1A1A; border-radius: 6px; padding: 10px 14px; margin-bottom: 16px; font-size: 0.85rem; color: #1A1A1A; font-family: 'IBM Plex Mono', monospace; box-shadow: 3px 3px 0px #1A1A1A;">
                        <b>Site Name:</b> {r_first['Site Name Surge']} &nbsp;|&nbsp; 
                        <b>Koordinat:</b> {r_first['Latitude']:.5f}, {r_first['Longitude']:.5f} &nbsp;|&nbsp; 
                        <b>Total Sektor:</b> {len(df_site_info)} &nbsp;|&nbsp; 
                        <b>Azimuth:</b> {az_str}°
                    </div>
                    ''', unsafe_allow_html=True)
                
                for idx, photo_item in enumerate(matched_photos, 1):
                    st.markdown(f'''
                    <div style="background: #F1F5F3; border: 1.5px solid #1A1A1A; border-radius: 6px; padding: 12px 16px; margin-bottom: 12px; box-shadow: 3px 3px 0 #1A1A1A; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                        <span style="font-weight: 700; color: #1A1A1A; font-family: 'IBM Plex Mono', monospace; font-size: 0.9rem;">
                            {photo_item['filename']}
                        </span>
                        <a href="{photo_item['view_url']}" target="_blank" style="color: #1A1A1A; text-decoration: none; font-size: 0.82rem; font-weight: 700; font-family: 'IBM Plex Mono', monospace;">
                            Buka di Google Drive
                        </a>
                    </div>
                    ''', unsafe_allow_html=True)
                    
                    with st.spinner(f"Memuat foto {photo_item['filename']}..."):
                        img_bytes = download_image_bytes(photo_item['id'])
                    
                    if img_bytes:
                        st.image(img_bytes, caption=f"Rekomendasi Tilting: {photo_item['filename']}", use_container_width=True)
                        
                        col_dl1, col_dl2 = st.columns([1, 1])
                        with col_dl1:
                            st.download_button(
                                label=f"Download {photo_item['filename']}",
                                data=img_bytes,
                                file_name=photo_item['filename'],
                                mime=photo_item['mime'] if photo_item['mime'] else "image/jpeg",
                                use_container_width=True,
                                type="primary",
                                icon=":material/download:",
                                key=f"dl_single_{photo_item['id']}"
                            )
                        with col_dl2:
                            st.link_button(
                                label="Buka File di Google Drive",
                                url=photo_item['view_url'],
                                icon=":material/open_in_new:",
                                use_container_width=True
                            )
                        st.markdown("<br>", unsafe_allow_html=True)
                    else:
                        st.warning(f"Tidak dapat memuat pratinjau gambar untuk {photo_item['filename']}.", icon=":material/warning:")
            else:
                st.warning(f"Foto Tilting Recommendation untuk Site ID {clean_selected} belum ditemukan di folder Google Drive.", icon=":material/warning:")
                st.markdown(f'''
                <div style="color: #4A4A4A; font-size: 0.88rem; font-family: 'IBM Plex Mono', monospace; margin-top: 8px;">
                    Pastikan nama file foto di Google Drive sesuai dengan format Site ID (contoh: <code>{clean_selected}.jpg</code> atau <code>{clean_selected}.jpeg</code>).
                    <br><br>
                    <a href="{DRIVE_FOLDER_URL}" target="_blank" style="color: #1A1A1A; font-weight: 800; text-decoration: underline;">
                        Buka Google Drive untuk Upload Foto
                    </a>
                </div>
                ''', unsafe_allow_html=True)
            
    else:
        st.markdown(
            '<div style="text-align: center; color: #4A4A4A; padding: 48px 24px; border: 1.5px dashed #1A1A1A; border-radius: 8px; background: #FFFFFF; box-shadow: 4px 4px 0px #1A1A1A;">'
            '<div style="display: inline-flex; align-items: center; justify-content: center; width: 48px; height: 48px; border-radius: 8px; background: #D6C7FF; border: 2px solid #1A1A1A; box-shadow: 3px 3px 0px #1A1A1A; margin-bottom: 12px;">'
            '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="3" rx="2"/><path d="M3 9h18"/><path d="M9 21V9"/></svg>'
            '</div>'
            '<div style="font-family: \'Comfortaa\', cursive; font-weight: 800; font-size: 1.1rem; color: #1A1A1A; margin-bottom: 4px;">Pilih Site ID</div>'
            '<p style="font-family: \'IBM Plex Mono\', monospace; font-size: 0.9rem; margin: 0;">Pilih salah satu <b>Site ID</b> pada kotak pencarian di atas untuk melihat dan mengunduh foto rekomendasi tilting.</p>'
            '</div>',
            unsafe_allow_html=True
        )

# ==============================
# TOOL KONTROL: SPOT CHECKER & SPOT GENERATOR
# ==============================
else:
    points = []

    if menu == "SSV Spot Checker":
        with st.container(border=True):
            st.markdown('<div class="card-attached-tab pink">input titik lapangan</div>', unsafe_allow_html=True)
            with st.expander("Petunjuk Format Data Titik Tes Lapangan", expanded=False):
                st.markdown("""
                Salin langsung tabel dari Excel atau Google Sheets. Format kolom otomatis mendeteksi Latitude dan Longitude.
                ```tsv
                Scenario    Speed    Target    Distance    Location    Latitude    Longitude
                Scenario 1  100      DL 300    1           Outdoor     -6.967333   110.128127
                ```
                """)

            with st.form("data_form", border=False):
                pasted_data = st.text_area(
                    "Paste your spreadsheet data here (Excel/Sheets):",
                    height=130,
                    placeholder="Scenario 1\t50-150\tDL 315\t1\tOutdoor\thigh dense residential\t-6.967333\t110.128127"
                )
                submit_btn = st.form_submit_button("Tampilkan Titik di Peta (Process Data)", use_container_width=True, icon=":material/my_location:")

            if pasted_data.strip():
                res, err, _ = parse_input_data(pasted_data)
                if err:
                    st.warning(err, icon=":material/warning:")
                elif res:
                    points = res
                    st.success(f"Berhasil membaca {len(points)} titik tes lapangan.", icon=":material/check_circle:")

    # [UI-ONLY] Site Selection Card (Attached tab inside container)
    with st.container(border=True):
        st.markdown('<div class="card-attached-tab amber">pencarian site id</div>', unsafe_allow_html=True)
        col1, col2 = st.columns([4, 1])
        site_list = sorted(df_bersih['Site ID Surge'].unique().tolist())

        with col1:
            selected_site = st.selectbox(
                "Cari Site ID:", 
                site_list, 
                index=None, 
                placeholder="Ketik Site ID di sini..."
            )

        with col2:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("Sync Data", use_container_width=True, icon=":material/sync:", help="Tarik data terbaru dari Google Sheets"):
                st.cache_data.clear()
                st.rerun()

    if selected_site:
        df_filtered = df_bersih[df_bersih['Site ID Surge'] == selected_site].reset_index(drop=True)
        site_name = df_filtered.iloc[0]['Site Name Surge']
        center_lon = float(df_filtered.iloc[0]['Longitude'])
        center_lat = float(df_filtered.iloc[0]['Latitude'])

        band_val = df_filtered.iloc[0].get('Band', 'n50')
        azimuths_str = ", ".join(df_filtered['Azimuth'].astype(int).astype(str).tolist())
        maps_url = f"https://www.google.com/maps/dir/?api=1&destination={center_lat},{center_lon}"

        # [UI-ONLY] Site Summary Header & Bento Grid (Attached tab inside container)
        with st.container(border=True):
            st.markdown('<div class="card-attached-tab mint">ringkasan site & telemetri</div>', unsafe_allow_html=True)
            header_html = f"""
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; margin-bottom: 14px;">
                <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
                    <span style="display: inline-flex; align-items: center; justify-content: center; width: 36px; height: 36px; border-radius: 6px; background: #8DD3DB; border: 1.5px solid #1A1A1A; box-shadow: 2.5px 2.5px 0px #1A1A1A;">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/></svg>
                    </span>
                    <h2 style="margin: 0; font-size: 1.35rem; font-weight: 800; color: #1A1A1A; font-family: 'Comfortaa', cursive;">{site_name}</h2>
                    <span class="badge-pill badge-pill-mint"><span class="pulse-dot"></span> DATABASE LIVE</span>
                    <span class="badge-pill badge-pill-lavender">WGS84 / EPSG:32749</span>
                </div>
                <div>
                    <a href="{maps_url}" target="_blank" style="display: inline-flex; align-items: center; gap: 6px; color: #1A1A1A; text-decoration: none; font-weight: 700; font-size: 0.82rem; font-family: 'IBM Plex Mono', monospace; background: #8DD3DB; border: 1.5px solid #1A1A1A; padding: 7px 14px; border-radius: 6px; box-shadow: 3.5px 3.5px 0px #1A1A1A;">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="6" cy="19" r="3"/><path d="M9 19h8.5a3.5 3.5 0 0 0 0-7h-11a3.5 3.5 0 0 1 0-7H15"/><circle cx="18" cy="5" r="3"/></svg> Rute Google Maps
                    </a>
                </div>
            </div>
            <div class="site-bento-grid">
                <div class="bento-chip" style="background: #8DD3DB;">
                    <span class="bento-chip-label">SITE ID</span>
                    <span class="bento-chip-val">{selected_site}</span>
                </div>
                <div class="bento-chip" style="background: #A9D6A0;">
                    <span class="bento-chip-label">TOTAL SECTOR</span>
                    <span class="bento-chip-val">{len(df_filtered)} Sektor</span>
                </div>
                <div class="bento-chip" style="background: #FFAE2B;">
                    <span class="bento-chip-label">AZIMUTH</span>
                    <span class="bento-chip-val">{azimuths_str}°</span>
                </div>
                <div class="bento-chip" style="background: #FFBCC4;">
                    <span class="bento-chip-label">COORDINATES</span>
                    <span class="bento-chip-val-coord">Lat: {center_lat:.5f}<br>Lon: {center_lon:.5f}</span>
                </div>
            </div>
            """
            st.markdown(header_html, unsafe_allow_html=True)

        # [UI-ONLY] Map Section Container (Attached tab inside container)
        with st.container(border=True):
            st.markdown('<div class="card-attached-tab toska">peta interaktif sektor</div>', unsafe_allow_html=True)

            # Legend Generator untuk Sektor
            legend_items_html = ""
            is_atp = menu in ["KMZ for ATP V2", "KMZ for ATP"]
            sec_palette = ['#e53935', '#00e676', '#ffd600', '#2979ff', '#d500f9'] if is_atp else ['#00ff00', '#ff0000', '#ffff00', '#0000ff', '#ff00ff']

            for sec_i, (_, r_sec) in enumerate(df_filtered.iterrows(), start=1):
                dot_col = sec_palette[(sec_i - 1) % len(sec_palette)]
                az_deg = int(r_sec['Azimuth'])
                pci_str = r_sec.get('PCI', '-')
                legend_items_html += (
                    f'<div class="legend-item">'
                    f'<span class="legend-dot" style="background-color: {dot_col};"></span>'
                    f'<span>Sec {sec_i}: <b style="color: #1A1A1A;">{az_deg}°</b> <span style="color: #4A4A4A;">(PCI {pci_str})</span></span>'
                    f'</div>'
                )

            map_title_html = (
                f'<div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; margin-bottom: 12px;">'
                f'<div style="display: flex; align-items: center; gap: 8px;">'
                f'<span style="display: inline-flex; align-items: center; justify-content: center; width: 30px; height: 30px; border-radius: 4px; background: #8DD3DB; border: 1.5px solid #1A1A1A; box-shadow: 2px 2px 0px #1A1A1A;">'
                f'<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/><path d="M2 12h20"/></svg>'
                f'</span>'
                f'<h3 style="margin: 0; color: #1A1A1A; font-family: \'Comfortaa\', cursive; font-weight: 800; font-size: 1.15rem;">Live Interactive Map Preview</h3>'
                f'</div>'
                f'<div class="legend-bar">'
                f'<span style="font-size: 0.72rem; color: #1A1A1A; text-transform: uppercase; font-family: \'IBM Plex Mono\', monospace; font-weight: 700;">SEKTOR:</span>'
                f'{legend_items_html}'
                f'</div>'
                f'</div>'
            )
            st.markdown(map_title_html, unsafe_allow_html=True)

            # Map Preview: dark_matter
            m = folium.Map(location=[center_lat, center_lon], zoom_start=16, tiles='CartoDB dark_matter', control_scale=True)

            # Tambahkan Google Satellite Layer
            folium.TileLayer(
                tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
                attr='Google',
                name='Google Satellite',
                overlay=False,
                control=True
            ).add_to(m)

            # Tambahkan Measure Control
            m.add_child(MeasureControl(position='topleft', primary_length_unit='meters', secondary_length_unit='kilometers'))

            # Tambahkan Locate Control
            LocateControl(
                position="topleft", 
                drawCircle=True,
                flyTo=True, 
                strings={"title": "Klik untuk terbang ke Lokasi Saya", "popup": "Posisi Anda Sekarang!"}
            ).add_to(m)

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
            fg_spots = folium.FeatureGroup(name='Titik Tes / Skenario', show=True)

            is_atp = menu in ["KMZ for ATP V2", "KMZ for ATP"]
            is_atp_v1 = (menu == "KMZ for ATP V1")
            folium.Marker([center_lat, center_lon], popup=site_name, tooltip=f"Pusat Site: {site_name}", icon=folium.Icon(color='lightgray', icon='info-sign')).add_to(m)

            ring_color = '#ffd600' if is_atp else 'white'
            line_color = '#ffd600' if is_atp else 'white'

            # Tambahkan RING (100m, 300m, 500m) ke peta web
            for r in [100, 300, 500]:
                folium.Circle(
                    location=[center_lat, center_lon],
                    radius=r,
                    color=ring_color,
                    weight=2 if is_atp else 1,
                    fill=False,
                    tooltip=f"Ring {r}m"
                ).add_to(fg_rings)

            sector_colors_atp = ['#e53935', '#00e676', '#ffd600', '#2979ff', '#d500f9']
            sector_colors_std = ['#00ff00', '#ff0000', '#ffff00', '#0000ff', '#ff00ff']
            chosen_colors = sector_colors_atp if is_atp else sector_colors_std

            x0, y0 = transformer_to_utm.transform(center_lon, center_lat)

            for sec_idx, (_, row) in enumerate(df_filtered.iterrows(), start=1):
                lon = float(row['Longitude'])
                lat = float(row['Latitude'])
                az = float(row['Azimuth'])
                bw = float(row['H Beamwidth'])

                # Sector polygon: untuk ATP dibuat full 100m mengikuti lingkaran ring 100m
                sec_radius = 100 if is_atp else 500
                sector, _, _ = create_sector(lon, lat, az, bw, sec_radius) 
                coords = [(y, x) for x, y in sector.exterior.coords]

                pci_val = row.get('PCI', '-')
                cell_name = row.get('Cell Name', '-')

                tooltip_html = f"<div style='min-width:120px; font-family:sans-serif;'><b>Sektor {sec_idx}</b><br>Azimuth: {az}°<br>PCI: {pci_val}<br>Sector: {cell_name}</div>"

                color = chosen_colors[(sec_idx - 1) % len(chosen_colors)]
                folium.Polygon(
                    locations=coords, color=color, fill=True, fill_opacity=0.6 if is_atp else 0.2,
                    weight=2 if is_atp else 1, tooltip=tooltip_html
                ).add_to(fg_sectors)

                # Line dari site ke 500m
                rad = math.radians(az)
                px_line = x0 + 500 * math.sin(rad)
                py_line = y0 + 500 * math.cos(rad)
                lon_line_end, lat_line_end = transformer_to_wgs.transform(px_line, py_line)

                folium.PolyLine(
                    locations=[[lat, lon], [lat_line_end, lon_line_end]],
                    color=line_color,
                    weight=2,
                    tooltip=f"Garis Azimuth Sektor {sec_idx} ({int(az)}°)"
                ).add_to(fg_lines)

                if is_atp:
                    for scen_idx, dist in enumerate([100, 300, 500], start=1):
                        px_spot = x0 + dist * math.sin(rad)
                        py_spot = y0 + dist * math.cos(rad)
                        lon_spot, lat_spot = transformer_to_wgs.transform(px_spot, py_spot)

                        folium.CircleMarker(
                            location=[lat_spot, lon_spot],
                            radius=5,
                            color='#ffd600',
                            fill=True,
                            fill_color='#ffd600',
                            fill_opacity=0.9,
                            tooltip=f"Sec{sec_idx}_Scen{scen_idx} ({dist}m)"
                        ).add_to(fg_spots)
                elif menu != "KMZ for ATP":
                    spot_counter = 1
                    for dist in [100, 300, 500]:
                        px_spot = x0 + dist * math.sin(rad)
                        py_spot = y0 + dist * math.cos(rad)
                        lon_spot, lat_spot = transformer_to_wgs.transform(px_spot, py_spot)

                        icon_color = "blue" if spot_counter == 2 else "orange"
                        folium.Marker(
                            location=[lat_spot, lon_spot],
                            tooltip=f"Sec{sec_idx}_Scen{spot_counter} ({dist}m)",
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

        # ==============================
        # [UI-ONLY] MINI ANALYTICS & RADAR PLOT CONTAINER
        # ==============================
        with st.container(border=True):
            st.markdown('<div class="card-attached-tab lavender">analisis sektor & telemetri jarak</div>', unsafe_allow_html=True)
            st.markdown("""
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 15px;">
                <span style="display: inline-flex; align-items: center; justify-content: center; width: 30px; height: 30px; border-radius: 4px; background: #D6C7FF; border: 1.5px solid #1A1A1A; box-shadow: 2px 2px 0px #1A1A1A;">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/></svg>
                </span>
                <h3 style="margin: 0; color: #1A1A1A; font-family: 'Comfortaa', cursive; font-weight: 800; font-size: 1.15rem;">Mini Analytics & Radar Azimuth</h3>
            </div>
            """, unsafe_allow_html=True)

            ana_col1, ana_col2 = st.columns([1, 1.5])

            with ana_col1:
                # Radar Chart for Azimuths
                df_radar = pd.DataFrame({
                    'r': [1] * len(df_filtered),
                    'theta': df_filtered['Azimuth'].astype(float),
                    'Sektor': [f"Sec {i+1}" for i in range(len(df_filtered))]
                })
                fig = px.line_polar(df_radar, r='r', theta='theta', text='Sektor', line_close=True, range_r=[0, 1.5], template='plotly_white')
                fig.update_traces(fill='toself', fillcolor='rgba(255, 174, 43, 0.35)', line=dict(color='#1A1A1A', width=2.5), marker=dict(size=9, color='#FFAE2B', line=dict(color='#1A1A1A', width=1.5)))
                fig.update_layout(polar=dict(angularaxis=dict(direction='clockwise', rotation=90)), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=20, b=20, l=20, r=20), height=300)
                st.plotly_chart(fig, use_container_width=True)

            with ana_col2:
                st.markdown("""
                <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 10px;">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/></svg>
                    <h4 style="margin: 0; color: #1A1A1A; font-family: 'Comfortaa', cursive; font-weight: 700; font-size: 1.05rem;">Jarak Aktual Titik Tes (Haversine)</h4>
                </div>
                """, unsafe_allow_html=True)
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
                    st.info("Belum ada data Titik Tes Lapangan yang dimasukkan.", icon=":material/info:")

        # ==============================
        # PROSES PEMBUATAN BERKAS KMZ (EXACT CUSTOMER TEMPLATE)
        # ==============================
        with st.status('Membangun File Super KMZ...', expanded=True) as status:
            st.write("Mempersiapkan metadata Site...")
            kml = simplekml.Kml()
            site_id = selected_site
            site_label = f"{site_name}" if is_atp else f"{site_id} - {site_name}"
            folder_site = kml.newfolder(name=site_label)
            folder_site.visibility = 1

            p_site = folder_site.newpoint(name=site_label)
            p_site.coords = [(center_lon, center_lat)]
            p_site.style.iconstyle.color = simplekml.Color.white
            p_site.style.iconstyle.scale = 0.8
            p_site.style.labelstyle.color = simplekml.Color.white
            p_site.style.labelstyle.scale = 1.0
            p_site.visibility = 1

            st.write("Membuat poligon Ring Radius (100m, 300m, 500m)...")
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

                if is_atp:
                    pol_ring.style.linestyle.color = simplekml.Color.yellow
                    pol_ring.style.linestyle.width = 2
                else:
                    pol_ring.style.linestyle.color = simplekml.Color.white
                    pol_ring.style.linestyle.width = 3
                pol_ring.style.polystyle.fill = 0

            folder_az = folder_site.newfolder(name="AZIMUTH" if not is_atp else "SECTOR & AZIMUTH")
            folder_az.visibility = 1

            if is_atp:
                folder_scen = folder_site.newfolder(name="SCENARIO SPOTS")
                folder_scen.visibility = 1
            elif not is_atp_v1:
                folder_spot = folder_site.newfolder(name="SPOT SSV")
                folder_spot.visibility = 1

            st.write("Membangun poligon Sektor dan Spot Area...")
            kml_colors_atp = [simplekml.Color.red, simplekml.Color.green, simplekml.Color.yellow, simplekml.Color.blue]
            kml_colors_std = [simplekml.Color.green, simplekml.Color.red, simplekml.Color.yellow, simplekml.Color.blue]

            for sec_idx, (_, row) in enumerate(df_filtered.iterrows(), start=1):
                lon = float(row['Longitude'])
                lat = float(row['Latitude'])
                az = float(row['Azimuth'])
                bw = float(row['H Beamwidth'])

                # Sektor wedge: 100m untuk ATP (full sampai ring 100m), 500m untuk SSV biasa
                sec_radius = 100 if is_atp else 500
                sector, _, _ = create_sector(lon, lat, az, bw, sec_radius)
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

                if is_atp:
                    chosen_kml_col = kml_colors_atp[(sec_idx - 1) % len(kml_colors_atp)]
                    pol.style.polystyle.color = simplekml.Color.changealphaint(210, chosen_kml_col)
                    pol.style.linestyle.color = simplekml.Color.black
                    pol.style.linestyle.width = 1
                else:
                    chosen_kml_col = kml_colors_std[(sec_idx - 1) % len(kml_colors_std)]
                    pol.style.polystyle.color = simplekml.Color.changealphaint(120, chosen_kml_col)

                rad = math.radians(az)
                px_line = x0 + 500 * math.sin(rad)
                py_line = y0 + 500 * math.cos(rad)

                line = folder_az.newlinestring(name=f"LINE_Sec{sec_idx}_{int(az)}")
                line.coords = [(lon, lat), transformer_to_wgs.transform(px_line, py_line)]
                if is_atp:
                    line.style.linestyle.color = simplekml.Color.yellow
                    line.style.linestyle.width = 2
                else:
                    line.style.linestyle.color = simplekml.Color.white
                    line.style.linestyle.width = 2
                line.visibility = 1

                if is_atp:
                    folder_sec_scen = folder_scen.newfolder(name=f"Sec {sec_idx}")
                    folder_sec_scen.visibility = 1
                    for scen_idx, dist in enumerate([100, 300, 500], start=1):
                        px_spot = x0 + dist * math.sin(rad)
                        py_spot = y0 + dist * math.cos(rad)
                        lon2, lat2 = transformer_to_wgs.transform(px_spot, py_spot)

                        scen_name = f"Sec{sec_idx}_Scen{scen_idx}"
                        pnt = folder_sec_scen.newpoint(name=scen_name)
                        pnt.coords = [(lon2, lat2)]
                        pnt.style.iconstyle.icon.href = "http://maps.google.com/mapfiles/kml/pushpin/ylw-pushpin.png"
                        pnt.style.iconstyle.scale = 0.8
                        pnt.style.labelstyle.color = simplekml.Color.yellow
                        pnt.style.labelstyle.scale = 0.9
                        pnt.visibility = 1
                elif not is_atp_v1:
                    folder_sec = folder_spot.newfolder(name=f"Sec {sec_idx}")
                    folder_sec.visibility = 1
                    spot_counter = 1

                    for dist in [100, 300, 500]:
                        px_spot = x0 + dist * math.sin(rad)
                        py_spot = y0 + dist * math.cos(rad)
                        lon2, lat2 = transformer_to_wgs.transform(px_spot, py_spot)

                        pnt = folder_sec.newpoint(name=f"Sec{sec_idx}_Scen{spot_counter}")
                        pnt.coords = [(lon2, lat2)]
                        pnt.style.iconstyle.icon.href = "http://maps.google.com/mapfiles/kml/pushpin/blue-pushpin.png" if spot_counter == 2 else "http://maps.google.com/mapfiles/kml/pushpin/ylw-pushpin.png"
                        pnt.visibility = 1
                        spot_counter += 1

            if points:
                st.write("Menambahkan Field Test Points ke dalam KMZ...")
                folder_points = folder_site.newfolder(name="TITIK TES LAPANGAN")
                folder_points.visibility = 1
                for i, pt in enumerate(points, 1):
                    p_spot = folder_points.newpoint(name=pt['name'])
                    p_spot.coords = [(pt['lon'], pt['lat'])]
                    p_spot.style.iconstyle.color = simplekml.Color.red
                    p_spot.visibility = 1
                    p_spot.description = pt['desc_html']

            if is_atp:
                kmz_name = f"ATP_V2_{site_id}_{datetime.now().strftime('%d%b%Y')}.kmz"
            elif is_atp_v1:
                kmz_name = f"ATP_V1_{site_id}_{datetime.now().strftime('%d%b%Y')}.kmz"
            else:
                kmz_name = f"SSV_{site_id}_{datetime.now().strftime('%d%b%Y')}.kmz"

            status.update(label="Super KMZ Berhasil Dibuat!", state="complete", expanded=False)

            kml.save("temp.kml")
            kmz_io = io.BytesIO()
            with zipfile.ZipFile(kmz_io, 'w', zipfile.ZIP_DEFLATED) as z:
                z.write("temp.kml", arcname="doc.kml")

            kmz_data = kmz_io.getvalue()

            if os.path.exists("temp.kml"):
                os.remove("temp.kml")

        def celebration():
            st.balloons()

        # [UI-ONLY] Large Symmetrical Download Buttons (Amber KMZ & Toska PDF)
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            st.download_button(
                label="Download File KMZ",
                data=kmz_data,
                file_name=kmz_name,
                mime="application/vnd.google-earth.kmz",
                use_container_width=True,
                type="primary",
                icon=":material/download:",
                on_click=celebration
            )

        with col_btn2:
            pdf_data = generate_pdf(site_id, site_name, df_filtered, dist_data if 'dist_data' in locals() else [])
            st.download_button(
                label="Download PDF Report",
                data=bytes(pdf_data),
                file_name=f"SSV_Report_{site_id}_{datetime.now().strftime('%d%b%Y')}.pdf",
                mime="application/pdf",
                use_container_width=True,
                type="primary",
                icon=":material/picture_as_pdf:",
                on_click=celebration
            )

    else:
        st.markdown(
            '<div style="text-align: center; color: #4A4A4A; padding: 48px 24px; border: 1.5px dashed #1A1A1A; border-radius: 8px; background: #FFFFFF; box-shadow: 4px 4px 0px #1A1A1A;">'
            '<div style="display: inline-flex; align-items: center; justify-content: center; width: 48px; height: 48px; border-radius: 8px; background: #FFAE2B; border: 2px solid #1A1A1A; box-shadow: 3px 3px 0px #1A1A1A; margin-bottom: 12px;">'
            '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4.5 10.5C3.5 12.5 3 14.5 3 17"/><path d="M19.5 10.5c1 2 1.5 4 1.5 6.5"/><path d="M6 18h12"/><path d="M12 2v20"/><path d="m8 6 8 8"/><path d="m16 6-8 8"/></svg>'
            '</div>'
            '<div style="font-family: \'Comfortaa\', cursive; font-weight: 800; font-size: 1.1rem; color: #1A1A1A; margin-bottom: 4px;">Pilih Site ID</div>'
            '<p style="font-family: \'IBM Plex Mono\', monospace; font-size: 0.85rem; margin: 0; color: #4A4A4A;">Gunakan kotak pencarian di atas untuk memulai visualisasi dan generate KMZ.</p>'
            '</div>',
            unsafe_allow_html=True
        )

# ==============================
# [UI-ONLY] Monospace Minimalist Footer
# ==============================
st.markdown("""
<div style="margin-top: 48px; padding-top: 18px; border-top: 1.5px solid #1A1A1A; text-align: center; font-family: 'IBM Plex Mono', monospace; font-size: 0.74rem; font-weight: 600; color: #4A4A4A;">
    Made with 💙 by Yusuf Nurhuda , LIKE KOMEN AND SUBREK 
</div>
""", unsafe_allow_html=True)
