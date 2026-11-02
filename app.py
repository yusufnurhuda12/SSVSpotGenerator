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
from tilting_manager import (
    fetch_gdrive_tilting_files,
    find_tilting_photos_for_site,
    download_image_bytes,
    create_tilting_zip,
    DRIVE_FOLDER_URL,
    FOLDER_ID
)

# ==============================
# KONFIGURASI WEB
# ==============================
st.set_page_config(page_title="SSV Spot Checker", layout="wide")

# ==============================
# DESIGN SYSTEM: MODERN INDUSTRIAL ENTERPRISE (LINEAR × VERCEL × DATADOG)
# Ground: #080c14 | Surface 1: #0d131f | Surface 2: #121a2b | Accent: #2563eb & #38bdf8
# Strict: Information Density, Readability, Visual Consistency
# ==============================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* Global Ground & Clean Canvas */
    html, body, .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        background-color: #080c14 !important;
        background-image: none !important;
        color: #f1f5f9 !important;
    }

    /* Hide Default Streamlit Header for Full Flush Application Ribbon */
    header[data-testid="stHeader"] {
        display: none !important;
    }

    /* Container Max Width for Focused Industrial Density */
    .block-container {
        max-width: 1140px !important;
        margin: 0 auto !important;
        padding-top: 1rem !important;
        padding-bottom: 3.5rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
    }

    /* Precision Scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: #080c14;
    }
    ::-webkit-scrollbar-thumb {
        background: #1c2638;
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #283750;
    }

    /* Precision Monospace for Technical Figures */
    .mono-data {
        font-family: 'JetBrains Mono', monospace !important;
        font-variant-numeric: tabular-nums !important;
        letter-spacing: -0.01em;
    }

    /* Headings - Linear Typography Hierarchy */
    h1 {
        text-align: left !important;
        color: #f8fafc !important;
        font-weight: 700 !important;
        font-size: 1.3rem !important;
        letter-spacing: -0.02em !important;
        margin: 0 !important;
        padding: 0 !important;
        line-height: 1.25 !important;
    }
    
    h2, h3, h4 {
        color: #f8fafc !important;
        font-weight: 600 !important;
        letter-spacing: -0.015em !important;
        margin-top: 0 !important;
    }

    .subtitle {
        text-align: left !important;
        color: #94a3b8 !important;
        font-size: 0.825rem !important;
        font-weight: 400 !important;
        letter-spacing: normal !important;
        margin-bottom: 0 !important;
        line-height: 1.45 !important;
    }

    /* Bento Panels & Cards - Clean Tone Steps with 1px Border and Unified Margin Rhythm */
    .panel-card, .glass-card {
        background-color: #0d131f !important;
        border: 1px solid #1c2638 !important;
        border-radius: 8px !important;
        padding: 16px 20px !important;
        margin-top: 0 !important;
        margin-bottom: 14px !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.04) !important;
        transition: border-color 0.15s ease !important;
    }
    .panel-card:hover, .glass-card:hover {
        border-color: #283750 !important;
    }

    /* Automatic Alignment for Action Buttons Beside Labeled Selectbox */
    div[data-testid="stHorizontalBlock"]:has(.stSelectbox) > div[data-testid="column"]:last-child .stButton button {
        margin-top: 28px !important;
    }

    /* Bento Micro-Stat Chip */
    .bento-chip {
        background: #080c14;
        border: 1px solid #1c2638;
        border-radius: 6px;
        padding: 8px 12px;
        display: flex;
        flex-direction: column;
        gap: 3px;
        transition: border-color 0.15s ease;
    }
    .bento-chip:hover {
        border-color: #283750;
    }
    .bento-chip-label {
        font-size: 0.68rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: 0.04em;
    }
    .bento-chip-val {
        font-size: 0.92rem;
        font-weight: 600;
        font-family: 'JetBrains Mono', monospace;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    /* Segmented Navigation & Control Buttons */
    .stButton>button {
        border-radius: 6px !important;
        font-weight: 500 !important;
        font-size: 0.84rem !important;
        padding: 8px 14px !important;
        min-height: 40px !important;
        box-shadow: none !important;
        transform: none !important;
        transition: all 0.15s ease !important;
    }
    .stButton>button:active, .stDownloadButton>button:active {
        transform: none !important;
    }

    /* Inactive Tab / Secondary Button */
    .stButton>button[kind="secondary"] {
        background-color: #0d131f !important;
        border: 1px solid #1c2638 !important;
        color: #94a3b8 !important;
    }
    .stButton>button[kind="secondary"]:hover {
        background-color: #121a2b !important;
        border-color: #283750 !important;
        color: #f8fafc !important;
    }

    /* Active Tab (Linear Segmented Control Style) */
    .stButton>button[kind="primary"] {
        background: #141d2e !important;
        background-color: #141d2e !important;
        border: 1px solid #2563eb !important;
        border-bottom: 2px solid #38bdf8 !important;
        border-radius: 6px !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.06) !important;
    }
    .stButton>button[kind="primary"]:hover {
        background: #182337 !important;
        background-color: #182337 !important;
        border-color: #3b82f6 !important;
    }

    /* Primary Action Buttons (Download / Submit) */
    .stDownloadButton>button[kind="primary"], div[data-testid="stFormSubmitButton"]>button {
        background: #2563eb !important;
        background-color: #2563eb !important;
        border: 1px solid #3b82f6 !important;
        border-radius: 6px !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 0.86rem !important;
        min-height: 40px !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.2) !important;
    }
    .stDownloadButton>button[kind="primary"]:hover, div[data-testid="stFormSubmitButton"]>button:hover {
        background: #1d4ed8 !important;
        background-color: #1d4ed8 !important;
        border-color: #60a5fa !important;
    }

    /* Secondary Download Buttons */
    .stDownloadButton>button[kind="secondary"] {
        background-color: #121a2b !important;
        border: 1px solid #233047 !important;
        color: #cbd5e1 !important;
        border-radius: 6px !important;
        font-weight: 500 !important;
        min-height: 40px !important;
    }
    .stDownloadButton>button[kind="secondary"]:hover {
        background-color: #182238 !important;
        border-color: #334460 !important;
        color: #ffffff !important;
    }

    /* Link Buttons */
    .stLinkButton>a {
        border-radius: 6px !important;
        font-weight: 500 !important;
        font-size: 0.825rem !important;
        background-color: #121a2b !important;
        border: 1px solid #233047 !important;
        color: #cbd5e1 !important;
        min-height: 40px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: all 0.15s ease !important;
    }
    .stLinkButton>a:hover {
        background-color: #182238 !important;
        border-color: #334460 !important;
        color: #ffffff !important;
    }

    /* Form Controls & Inputs - Crisp 1px Borders with Full 4-State System */
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #080c14 !important;
        border: 1px solid #1c2638 !important;
        border-radius: 6px !important;
        color: #f1f5f9 !important;
        min-height: 40px !important;
        padding-left: 10px !important;
        padding-right: 10px !important;
        box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.35) !important;
        transition: border-color 0.15s ease, box-shadow 0.15s ease, background-color 0.15s ease !important;
    }
    .stSelectbox div[data-baseweb="select"] > div:hover {
        border-color: #283750 !important;
        background-color: #0c121e !important;
        box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(40, 55, 80, 0.3) !important;
        cursor: pointer !important;
    }
    .stSelectbox div[data-baseweb="select"] > div:hover svg {
        fill: #cbd5e1 !important;
    }
    .stSelectbox div[data-baseweb="select"] > div:focus-within,
    .stSelectbox div[data-baseweb="select"][aria-expanded="true"] > div {
        border-color: #38bdf8 !important;
        background-color: #0d1522 !important;
        box-shadow: 0 0 0 1px #38bdf8, 0 0 10px rgba(56, 189, 248, 0.18) !important;
    }
    .stSelectbox div[data-baseweb="select"] > div:focus-within svg,
    .stSelectbox div[data-baseweb="select"][aria-expanded="true"] svg {
        fill: #38bdf8 !important;
    }
    .stSelectbox div[data-baseweb="select"][aria-invalid="true"] > div,
    .stSelectbox div[data-baseweb="select"] > div[aria-invalid="true"],
    .stSelectbox.has-error div[data-baseweb="select"] > div {
        border-color: #f43f5e !important;
        background-color: #160a0e !important;
        box-shadow: 0 0 0 1px #f43f5e, 0 0 8px rgba(244, 63, 94, 0.25) !important;
    }
    .stSelectbox div[data-baseweb="select"][aria-invalid="true"] svg,
    .stSelectbox.has-error svg {
        fill: #f43f5e !important;
    }
    .stSelectbox svg {
        fill: #94a3b8 !important;
        transition: fill 0.15s ease !important;
    }
    .stSelectbox label[data-testid="stWidgetLabel"] p {
        font-family: 'Inter', sans-serif !important;
        font-size: 0.8125rem !important;
        font-weight: 500 !important;
        color: #cbd5e1 !important;
        margin-bottom: 2px !important;
    }

    /* Text Input 4-State System Consistency */
    .stTextInput input {
        background-color: #080c14 !important;
        border: 1px solid #1c2638 !important;
        border-radius: 6px !important;
        color: #f1f5f9 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.84rem !important;
        min-height: 40px !important;
        box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.35) !important;
        transition: border-color 0.15s ease, box-shadow 0.15s ease, background-color 0.15s ease !important;
    }
    .stTextInput input:hover {
        border-color: #283750 !important;
        background-color: #0c121e !important;
    }
    .stTextInput input:focus {
        border-color: #38bdf8 !important;
        background-color: #0d1522 !important;
        box-shadow: 0 0 0 1px #38bdf8, 0 0 10px rgba(56, 189, 248, 0.18) !important;
    }
    .stTextInput input[aria-invalid="true"] {
        border-color: #f43f5e !important;
        background-color: #160a0e !important;
        box-shadow: 0 0 0 1px #f43f5e, 0 0 8px rgba(244, 63, 94, 0.25) !important;
    }

    /* Dropdown Popover Menu (Dark Theme) */
    div[data-baseweb="popover"], div[data-baseweb="popover"] > div {
        background-color: #0d131f !important;
        border: 1px solid #1c2638 !important;
        border-radius: 6px !important;
        color: #f1f5f9 !important;
    }
    ul[data-baseweb="menu"] {
        background-color: #0d131f !important;
    }
    li[data-baseweb="menu-item"] {
        color: #cbd5e1 !important;
        font-size: 0.825rem !important;
        font-family: 'Inter', sans-serif !important;
    }
    li[data-baseweb="menu-item"]:hover {
        background-color: #162035 !important;
        color: #ffffff !important;
    }

    .stTextArea textarea {
        background-color: #080c14 !important;
        border: 1px solid #1c2638 !important;
        border-radius: 6px !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.8125rem !important;
        color: #e2e8f0 !important;
        box-shadow: none !important;
        transition: border-color 0.15s ease !important;
    }
    .stTextArea textarea:focus {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 0 1px #38bdf8 !important;
    }

    /* Status Badges - Datadog Telemetry Style */
    .live-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 3px 8px;
        background: rgba(16, 185, 129, 0.08);
        border: 1px solid rgba(16, 185, 129, 0.25);
        border-radius: 4px;
        color: #34d399;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        font-weight: 500;
        letter-spacing: 0.02em;
    }
    .pulse-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background-color: #10b981;
    }

    /* Map Legend Bar - Clean Horizontal Strip */
    .legend-bar {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        background: #080c14;
        border: 1px solid #1c2638;
        border-radius: 6px;
        padding: 5px 8px;
        align-items: center;
        font-size: 0.75rem;
    }
    .legend-item {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 2px 7px;
        background: #121a2b;
        border: 1px solid #233047;
        border-radius: 4px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        color: #cbd5e1;
    }
    .legend-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
    }

    /* Map Viewport Frame */
    iframe {
        border-radius: 6px !important;
        border: 1px solid #1c2638 !important;
    }

    /* Streamlit Expander - Clean Accordion */
    .streamlit-expanderHeader {
        background-color: #0d131f !important;
        border: 1px solid #1c2638 !important;
        border-radius: 6px !important;
        color: #cbd5e1 !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
    }
    .streamlit-expanderContent {
        border: 1px solid #1c2638 !important;
        border-top: none !important;
        border-bottom-left-radius: 6px !important;
        border-bottom-right-radius: 6px !important;
        background-color: #080c14 !important;
        padding: 14px !important;
    }

    /* Table Component Adjustments */
    [data-testid="stDataFrame"] {
        border: 1px solid #1c2638 !important;
        border-radius: 6px !important;
        overflow: hidden;
    }
    
    /* Clean Instruction Table for SSV Spot Checker */
    .instruction-table-wrapper {
        overflow-x: auto;
        margin: 12px 0;
        border-radius: 6px;
        border: 1px solid #1c2638;
    }
    .instruction-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.8rem;
        background-color: #080c14;
        color: #cbd5e1;
    }
    .instruction-table th {
        background-color: #121a2b;
        color: #94a3b8;
        font-weight: 600;
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.03em;
        padding: 8px 10px;
        border: 1px solid #1c2638;
        text-align: center;
        font-family: 'JetBrains Mono', monospace;
    }
    .instruction-table td {
        padding: 6px 10px;
        border: 1px solid #1c2638;
        text-align: center;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
    }
    .instruction-table td.scenario-header {
        background-color: #0d131f;
        color: #f1f5f9;
        font-weight: 600;
    }

    /* Streamlit Status Box Styling */
    div[data-testid="stStatusWidget"] {
        background-color: #0d131f !important;
        border: 1px solid #1c2638 !important;
        border-radius: 6px !important;
    }

    /* Responsive Laptop Screen Optimization */
    @media screen and (max-width: 1366px) {
        .block-container {
            max-width: 100% !important;
            padding-left: 1.25rem !important;
            padding-right: 1.25rem !important;
            padding-top: 1rem !important;
        }
        .stButton>button {
            font-size: 0.8125rem !important;
            padding: 7px 10px !important;
            white-space: nowrap !important;
        }
        .bento-chip {
            padding: 6px 10px !important;
        }
        .bento-chip-val {
            font-size: 0.875rem !important;
        }
    }
    @media screen and (max-width: 992px) {
        .stButton>button {
            font-size: 0.775rem !important;
            padding: 6px 8px !important;
        }
        .legend-bar {
            font-size: 0.7rem !important;
            gap: 4px !important;
        }
        .legend-item {
            font-size: 0.68rem !important;
            padding: 2px 5px !important;
        }
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

        # Ekstrak angka sektor dan skenario untuk format SecX_ScenY
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
# VECTOR SVG ICON SET (NO EMOJIS)
# ==============================
SVG_ICONS = {
    "tower": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v20"/><path d="M8 22h8"/><path d="M9 10h6"/><path d="M7 16h10"/><path d="M5 6a10 10 0 0 1 14 0"/><path d="M2 3a15 15 0 0 1 20 0"/></svg>',
    "layers": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg>',
    "target": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="4"/><circle cx="12" cy="12" r="1" fill="currentColor"/><line x1="12" y1="1" x2="12" y2="4"/><line x1="12" y1="20" x2="12" y2="23"/><line x1="1" y1="12" x2="4" y2="12"/><line x1="20" y1="12" x2="23" y2="12"/></svg>',
    "crosshair": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="4"/><circle cx="12" cy="12" r="1" fill="currentColor"/><line x1="12" y1="1" x2="12" y2="4"/><line x1="12" y1="20" x2="12" y2="23"/><line x1="1" y1="12" x2="4" y2="12"/><line x1="20" y1="12" x2="23" y2="12"/></svg>',
    "angle": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 21h18"/><path d="M5 20 18 5"/><path d="M14 5h4v4"/><path d="M11 20a6 6 0 0 0-3-4"/><circle cx="5" cy="20" r="1.5" fill="currentColor"/></svg>',
    "folder": '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: -2px; margin-right: 4px;"><path d="M4 20h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.93a2 2 0 0 1-1.66-.9l-.82-1.2A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13c0 1.1.9 2 2 2Z"/></svg>',
    "pin": '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: -2px; margin-right: 4px;"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/></svg>',
    "image": '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: -2px; margin-right: 4px;"><rect width="18" height="18" x="3" y="3" rx="2" ry="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/></svg>',
    "map": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: -2px; margin-right: 6px;"><polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21"/><line x1="9" y1="3" x2="9" y2="18"/><line x1="15" y1="6" x2="15" y2="21"/></svg>',
    "chart": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: -2px; margin-right: 6px;"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>',
    "route": '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: -2px; margin-right: 4px;"><circle cx="6" cy="19" r="3"/><path d="M9 19h8.5a3.5 3.5 0 0 0 0-7h-11a3.5 3.5 0 0 1 0-7H15"/><circle cx="18" cy="5" r="3"/></svg>',
    "download": '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: -2px; margin-right: 6px;"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>'
}

# ==============================
# HEADER & TOP MENU NAVIGATION
# ==============================
st.markdown(f'''
<div class="panel-card" style="padding: 12px 18px;">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
        <div style="display: flex; align-items: center; gap: 10px; white-space: nowrap;">
            <span style="display: inline-flex; align-items: center; justify-content: center; width: 30px; height: 30px; border-radius: 6px; background: #121a2b; border: 1px solid #233047; color: #38bdf8; box-shadow: inset 0 1px 0 rgba(255,255,255,0.06); flex-shrink: 0;">
                {SVG_ICONS["tower"]}
            </span>
            <div style="display: flex; align-items: baseline; gap: 8px;">
                <span style="font-weight: 700; font-size: 0.95rem; color: #f8fafc; letter-spacing: -0.01em;">SSV STUDIO</span>
                <span style="color: #64748b; font-size: 0.75rem; font-family: 'JetBrains Mono', monospace;">• Fiberhome RF Console v2.6</span>
            </div>
        </div>
        <div style="display: flex; align-items: center; gap: 8px; white-space: nowrap;">
            <span class="live-badge"><span class="pulse-dot"></span> DATABASE LIVE</span>
            <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #64748b; background: #080c14; padding: 3px 8px; border-radius: 4px; border: 1px solid #1c2638;">
                WGS84 / EPSG:32749
            </span>
        </div>
    </div>
</div>
''', unsafe_allow_html=True)

# Normalize legacy emoji session state
if 'active_menu' not in st.session_state:
    st.session_state.active_menu = "SSV Spot Generator"
else:
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
    if st.button("SSV Spot Generator", use_container_width=True, type=btn_type1):
        st.session_state.active_menu = "SSV Spot Generator"
        st.rerun()

with menu_col2:
    btn_type2 = "primary" if st.session_state.active_menu in ["KMZ for ATP V2", "KMZ for ATP"] else "secondary"
    if st.button("KMZ for ATP V2", use_container_width=True, type=btn_type2):
        st.session_state.active_menu = "KMZ for ATP V2"
        st.rerun()

with menu_col3:
    btn_type3 = "primary" if st.session_state.active_menu == "SSV Spot Checker" else "secondary"
    if st.button("SSV Spot Checker", use_container_width=True, type=btn_type3):
        st.session_state.active_menu = "SSV Spot Checker"
        st.rerun()

with menu_col4:
    btn_type4 = "primary" if st.session_state.active_menu == "Tilting Recommendation" else "secondary"
    if st.button("Tilting Recommendation", use_container_width=True, type=btn_type4):
        st.session_state.active_menu = "Tilting Recommendation"
        st.rerun()

menu = st.session_state.active_menu

titles_map = {
    "SSV Spot Generator": ("SSV Spot Generator", "Render KMZ sektoral lengkap dengan garis azimuth dan panduan titik uji secara otomatis.", SVG_ICONS["tower"]),
    "KMZ for ATP V2": ("KMZ for ATP V2", "File KMZ siap pakai untuk dokumen ATP, lengkap dengan sektor 100m dan titik skenario.", SVG_ICONS["layers"]),
    "KMZ for ATP": ("KMZ for ATP V2", "File KMZ siap pakai untuk dokumen ATP, lengkap dengan sektor 100m dan titik skenario.", SVG_ICONS["layers"]),
    "KMZ for ATP V1": ("KMZ for ATP V1", "File KMZ berformat ringkas khusus untuk kebutuhan pelaporan ATP awal.", SVG_ICONS["layers"]),
    "SSV Spot Checker": ("SSV Spot Checker", "Validasi koordinat hasil uji lapangan langsung dengan posisi sektor aktual di peta.", SVG_ICONS["target"]),
    "Tilting Recommendation": ("Tilting Recommendation", "Unduh dan pratinjau foto rekomendasi tilting antena berdasarkan Site ID langsung dari Google Drive.", SVG_ICONS["angle"])
}
cur_title, cur_sub, cur_icon = titles_map.get(menu, ("SSV Spot Generator", "Otomasi pemetaan telekomunikasi dan pengolahan KMZ.", SVG_ICONS["tower"]))

st.markdown(f'''
<div class="panel-card">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
        <div style="display: flex; align-items: center; gap: 14px;">
            <span style="display: inline-flex; align-items: center; justify-content: center; width: 40px; height: 40px; border-radius: 8px; background: #121a2b; border: 1px solid #233047; color: #38bdf8; flex-shrink: 0; box-shadow: inset 0 1px 0 rgba(255,255,255,0.06);">
                {cur_icon}
            </span>
            <div>
                <h1 style="margin: 0; font-size: 1.25rem; font-weight: 700; color: #f8fafc; letter-spacing: -0.015em;">{cur_title}</h1>
                <div class="subtitle" style="margin-top: 3px;">{cur_sub}</div>
            </div>
        </div>
        <div style="display: flex; align-items: center; gap: 6px;">
            <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #94a3b8; background: #080c14; padding: 4px 10px; border-radius: 4px; border: 1px solid #1c2638;">
                MODULE ONLINE
            </span>
        </div>
    </div>
</div>
''', unsafe_allow_html=True)

with st.spinner('Mempersiapkan data...'):
    try:
        df_bersih = load_and_clean_data(SHEET_URL)
    except Exception as e:
        st.error(f"Gagal menarik data: {e}")
        st.stop()

# ==============================
# MENU: TILTING RECOMMENDATION
# ==============================
if menu == "Tilting Recommendation":
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    
    with st.spinner('Mengambil data foto rekomendasi tilting dari Google Drive...'):
        try:
            tilting_files = fetch_gdrive_tilting_files()
        except Exception as e:
            tilting_files = {}
    
    total_photos = len(tilting_files)
    
    # Status Banner
    st.markdown(f'''
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; margin-bottom: 16px; padding-bottom: 14px; border-bottom: 1px solid #1c2638;">
        <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
            <span class="live-badge"><span class="pulse-dot"></span> GOOGLE DRIVE TERHUBUNG</span>
            <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #cbd5e1; background: #080c14; padding: 3px 10px; border-radius: 4px; border: 1px solid #1c2638;">
                {SVG_ICONS["folder"]} {total_photos} Foto Tersedia
            </span>
        </div>
        <div>
            <a href="{DRIVE_FOLDER_URL}" target="_blank" style="display: inline-flex; align-items: center; gap: 6px; color: #38bdf8; text-decoration: none; font-weight: 500; font-size: 0.8rem; background: #121a2b; border: 1px solid #233047; padding: 6px 14px; border-radius: 6px; transition: all 0.15s ease;">
                Buka Folder Google Drive ↗
            </a>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Selection Controls
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
        if st.button("Sync Drive", use_container_width=True, help="Tarik ulang daftar foto terbaru dari Google Drive"):
            st.cache_data.clear()
            st.rerun()
            
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Detail View when a Site is Selected
    if selected_option:
        clean_selected = selected_option.replace(" (Foto Tersedia)", "").strip()
        matched_photos = find_tilting_photos_for_site(clean_selected, tilting_files)
        df_site_info = df_bersih[df_bersih['Site ID Surge'].str.upper() == clean_selected.upper()]
        
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        
        if matched_photos:
            st.markdown(f'''
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; margin-bottom: 14px; padding-bottom: 12px; border-bottom: 1px solid #1c2638;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="display: inline-flex; align-items: center; justify-content: center; width: 30px; height: 30px; border-radius: 6px; background: #121a2b; border: 1px solid #233047; color: #38bdf8;">
                        {SVG_ICONS["pin"]}
                    </span>
                    <div>
                        <h2 style="margin: 0; font-size: 1.15rem; font-weight: 600; color: #f8fafc; letter-spacing: -0.01em;">Site ID: <span style="color: #38bdf8;">{clean_selected}</span></h2>
                        <div style="color: #94a3b8; font-size: 0.8rem; margin-top: 2px;">
                            Ditemukan <b style="color: #34d399;">{len(matched_photos)} berkas rekomendasi tilting</b> untuk site ini.
                        </div>
                    </div>
                </div>
                <span class="live-badge"><span class="pulse-dot"></span> FOTO SIAP UNDUH</span>
            </div>
            ''', unsafe_allow_html=True)
            
            if not df_site_info.empty:
                r_first = df_site_info.iloc[0]
                az_str = ", ".join(df_site_info['Azimuth'].astype(int).astype(str).tolist())
                st.markdown(f'''
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 10px; margin-bottom: 14px;">
                    <div class="bento-chip">
                        <span class="bento-chip-label">SITE NAME</span>
                        <span class="bento-chip-val" style="color: #f1f5f9;">{r_first['Site Name Surge']}</span>
                    </div>
                    <div class="bento-chip">
                        <span class="bento-chip-label">TOTAL SECTOR</span>
                        <span class="bento-chip-val" style="color: #38bdf8;">{len(df_site_info)} Cells</span>
                    </div>
                    <div class="bento-chip">
                        <span class="bento-chip-label">AZIMUTH</span>
                        <span class="bento-chip-val" style="color: #fbbf24;">{az_str}°</span>
                    </div>
                    <div class="bento-chip">
                        <span class="bento-chip-label">COORDINATES</span>
                        <span class="bento-chip-val" style="color: #94a3b8; font-size: 0.78rem;">{r_first['Latitude']:.5f}, {r_first['Longitude']:.5f}</span>
                    </div>
                </div>
                ''', unsafe_allow_html=True)
            
            for idx, photo_item in enumerate(matched_photos, 1):
                st.markdown(f'''
                <div style="background: #080c14; border: 1px solid #1c2638; border-radius: 6px; padding: 10px 14px; margin-bottom: 12px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                        <span style="font-weight: 500; color: #f1f5f9; font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; display: flex; align-items: center; gap: 6px;">
                            {SVG_ICONS["image"]} <span>{photo_item['filename']}</span>
                        </span>
                        <a href="{photo_item['view_url']}" target="_blank" style="color: #38bdf8; text-decoration: none; font-size: 0.78rem; font-weight: 500;">
                            Buka di Google Drive ↗
                        </a>
                    </div>
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
                            key=f"dl_single_{photo_item['id']}"
                        )
                    with col_dl2:
                        st.link_button(
                            label="Buka File di Google Drive",
                            url=photo_item['view_url'],
                            use_container_width=True
                        )
                else:
                    st.warning(f"Tidak dapat memuat pratinjau gambar untuk {photo_item['filename']}.")
        else:
            st.warning(f"Foto Tilting Recommendation untuk Site ID {clean_selected} belum ditemukan di folder Google Drive.")
            st.markdown(f'''
            <div style="color: #94a3b8; font-size: 0.85rem; margin-top: 8px;">
                Pastikan nama file foto di Google Drive sesuai dengan format Site ID (contoh: <code>{clean_selected}.jpg</code> atau <code>{clean_selected}.jpeg</code>).
                <br><br>
                <a href="{DRIVE_FOLDER_URL}" target="_blank" style="color: #38bdf8; font-weight: 500; text-decoration: none;">
                    Buka Google Drive untuk Upload Foto ↗
                </a>
            </div>
            ''', unsafe_allow_html=True)
            
        st.markdown('</div>', unsafe_allow_html=True)
        
    else:
        st.markdown(
            f'<div class="panel-card" style="text-align: center; padding: 48px 24px; border-style: dashed; border-color: #1c2638; background: #0a0f1a;">'
            f'<div style="display: inline-flex; align-items: center; justify-content: center; width: 48px; height: 48px; border-radius: 10px; background: #121a2b; border: 1px solid #233047; color: #38bdf8; margin-bottom: 14px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">'
            f'{SVG_ICONS["angle"]}'
            f'</div>'
            f'<div style="color: #f8fafc; font-weight: 600; font-size: 1rem; margin-bottom: 4px; letter-spacing: -0.01em;">Awaiting Site Selection</div>'
            f'<p style="color: #64748b; font-size: 0.8125rem; margin: 0 auto; max-width: 440px; line-height: 1.5;">Ketik atau pilih Site ID pada kotak pencarian di atas untuk melihat dan mengunduh foto rekomendasi tilting antena.</p>'
            f'</div>',
            unsafe_allow_html=True
        )

else:

    # ==============================
    # TOOL KONTROL (CENTERED)
    # ==============================
    points = []

    if menu == "SSV Spot Checker":
        with st.expander("Petunjuk Format Data Uji Lapangan", expanded=False):
            st.markdown("""
            <div style="color: #cbd5e1; font-size: 0.85rem; margin-bottom: 10px;">
                <strong>Panduan Salin-Tempel:</strong> Salin tabel langsung dari spreadsheet (Excel / Google Sheets) seperti contoh format berikut:
            </div>
            <div class="instruction-table-wrapper">
                <table class="instruction-table">
                    <thead>
                        <tr>
                            <th colspan="8" style="background: #1e293b; color: #f8fafc; font-weight: 600; font-size: 0.8rem; letter-spacing: 0.02em;">CONTOH FORMAT TABEL DATA UJI</th>
                        </tr>
                        <tr>
                            <th>Scenario</th>
                            <th>Distance to BTS (m)</th>
                            <th>Target (Mbps)</th>
                            <th>Sector</th>
                            <th>Position</th>
                            <th>Category</th>
                            <th>Latitude</th>
                            <th>Longitude</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td rowspan="3" class="scenario-header">Scenario 1</td>
                            <td rowspan="3">50-150</td>
                            <td rowspan="3">DL 315</td>
                            <td>1</td><td>Outdoor</td><td>high dense res.</td><td>-6.8622</td><td>109.1379</td>
                        </tr>
                        <tr><td>2</td><td>Outdoor</td><td>high dense res.</td><td>-6.8638</td><td>109.1375</td></tr>
                        <tr><td>3</td><td>Outdoor</td><td>high dense res.</td><td>-6.8626</td><td>109.1364</td></tr>
                        <tr>
                            <td rowspan="3" class="scenario-header">Scenario 2</td>
                            <td rowspan="3">250-350</td>
                            <td rowspan="3">DL 150</td>
                            <td>1</td><td>Outdoor</td><td>high dense res.</td><td>-6.8609</td><td>109.1392</td>
                        </tr>
                        <tr><td>2</td><td>Outdoor</td><td>high dense res.</td><td>-6.8654</td><td>109.1379</td></tr>
                        <tr><td>3</td><td>Outdoor</td><td>high dense res.</td><td>-6.8621</td><td>109.1344</td></tr>
                        <tr>
                            <td rowspan="3" class="scenario-header">Scenario 3</td>
                            <td rowspan="3">400-500</td>
                            <td rowspan="3">DL 50</td>
                            <td>1</td><td>Outdoor</td><td>high dense res.</td><td>-6.8597</td><td>109.1404</td>
                        </tr>
                        <tr><td>2</td><td>Outdoor</td><td>high dense res.</td><td>-6.8672</td><td>109.1384</td></tr>
                        <tr><td>3</td><td>Outdoor</td><td>high dense res.</td><td>-6.8616</td><td>109.1329</td></tr>
                    </tbody>
                </table>
            </div>
            <ol style="color: #94a3b8; font-size: 0.8125rem; line-height: 1.6; margin: 10px 0 0 18px; padding: 0;">
                <li>Sorot sel tabel pada file spreadsheet Anda.</li>
                <li>Tekan <code style="color: #cbd5e1; background: #161e2e; padding: 2px 6px; border-radius: 4px;">Ctrl+C</code> lalu tempelkan (<code style="color: #cbd5e1; background: #161e2e; padding: 2px 6px; border-radius: 4px;">Ctrl+V</code>) ke kotak input di bawah.</li>
                <li>Klik tombol <strong>Tampilkan Titik di Peta (Process Data)</strong>.</li>
                <li>Pilih Site ID tujuan di kotak pencarian untuk membuka visualisasi peta interaktif.</li>
                <li>Klik <strong>Download File KMZ</strong> untuk mengunduh KMZ gabungan titik uji dan konfigurasi sektor.</li>
            </ol>
            """, unsafe_allow_html=True)

        with st.form("data_form", border=False):
            pasted_data = st.text_area("Tempel data tabel spreadsheet di sini (Excel / Google Sheets):", height=130, placeholder="Scenario 1\t50-150\tDL 315\t1\tOutdoor\thigh dense residential\t-6.967333\t110.128127")
            submit_btn = st.form_submit_button("Tampilkan Titik di Peta (Process Data)", use_container_width=True)

        if pasted_data.strip():
            res, err, _ = parse_input_data(pasted_data)
            if err:
                st.warning(err)
            elif res:
                points = res
                st.success(f"Berhasil membaca {len(points)} titik tes lapangan.")

    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    col1, col2 = st.columns([4, 1])
    site_list = sorted(df_bersih['Site ID Surge'].unique().tolist())

    with col1:
        selected_site = st.selectbox(
            "Cari Site ID:", 
            site_list, 
            index=None, 
            placeholder="Ketik Site ID di sini (contoh: 32CBN_0224)..."
        )

    with col2:
        if st.button("Sync Data", use_container_width=True, help="Tarik data terbaru dari Google Sheets"):
            st.cache_data.clear()
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    if selected_site:
        df_filtered = df_bersih[df_bersih['Site ID Surge'] == selected_site].reset_index(drop=True)
        site_name = df_filtered.iloc[0]['Site Name Surge']
        center_lon = float(df_filtered.iloc[0]['Longitude'])
        center_lat = float(df_filtered.iloc[0]['Latitude'])

        band_val = df_filtered.iloc[0].get('Band', 'n50')
        azimuths_str = ", ".join(df_filtered['Azimuth'].astype(int).astype(str).tolist())
        maps_url = f"https://www.google.com/maps/dir/?api=1&destination={center_lat},{center_lon}"

        header_html = (
            f'<div class="panel-card" style="padding: 16px 20px;">'
            f'<div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; margin-bottom: 12px; padding-bottom: 12px; border-bottom: 1px solid #1c2638;">'
            f'<div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">'
            f'<span style="display: inline-flex; align-items: center; justify-content: center; width: 30px; height: 30px; border-radius: 6px; background: #121a2b; border: 1px solid #233047; color: #38bdf8;">'
            f'{SVG_ICONS["pin"]}'
            f'</span>'
            f'<div>'
            f'<h2 style="margin: 0; font-size: 1.15rem; font-weight: 600; color: #f8fafc; letter-spacing: -0.01em;">{site_name}</h2>'
            f'</div>'
            f'<span class="live-badge" style="margin-left: 4px;"><span class="pulse-dot"></span> SURGE LLD FIBERHOME</span>'
            f'</div>'
            f'<div>'
            f'<a href="{maps_url}" target="_blank" style="display: inline-flex; align-items: center; gap: 6px; color: #38bdf8; text-decoration: none; font-weight: 500; font-size: 0.8rem; background: #121a2b; border: 1px solid #233047; padding: 6px 14px; border-radius: 6px; transition: all 0.15s ease;">'
            f'{SVG_ICONS["route"]}<span>Rute Google Maps ↗</span>'
            f'</a>'
            f'</div>'
            f'</div>'
            f'<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 10px;">'
            f'<div class="bento-chip">'
            f'<span class="bento-chip-label">SITE ID</span>'
            f'<span class="bento-chip-val" style="color: #38bdf8;">{selected_site}</span>'
            f'</div>'
            f'<div class="bento-chip">'
            f'<span class="bento-chip-label">TOTAL SECTOR</span>'
            f'<span class="bento-chip-val" style="color: #f1f5f9;">{len(df_filtered)} Cells</span>'
            f'</div>'
            f'<div class="bento-chip">'
            f'<span class="bento-chip-label">AZIMUTH</span>'
            f'<span class="bento-chip-val" style="color: #fbbf24;">{azimuths_str}°</span>'
            f'</div>'
            f'<div class="bento-chip">'
            f'<span class="bento-chip-label">COORDINATES</span>'
            f'<span class="bento-chip-val" style="color: #94a3b8; font-size: 0.78rem;">{center_lat:.5f}, {center_lon:.5f}</span>'
            f'</div>'
            f'</div>'
            f'</div>'
        )
        st.markdown(header_html, unsafe_allow_html=True)
        
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)

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
                f'<span>Sec {sec_i}: <b>{az_deg}°</b> <span style="color: #64748b;">(PCI {pci_str})</span></span>'
                f'</div>'
            )

        map_title_html = (
            f'<div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; margin-bottom: 12px;">'
            f'<div style="font-weight: 600; color: #f8fafc; font-size: 0.95rem; display: flex; align-items: center; gap: 8px;">'
            f'<span style="color: #38bdf8;">{SVG_ICONS["map"]}</span>'
            f'<span>Peta Interaktif Sektor</span>'
            f'</div>'
            f'<div class="legend-bar">'
            f'<span style="font-size: 0.7rem; color: #64748b; font-weight: 600; text-transform: uppercase; font-family: \'JetBrains Mono\', monospace;">SEKTOR:</span>'
            f'{legend_items_html}'
            f'</div>'
            f'</div>'
        )
        st.markdown(map_title_html, unsafe_allow_html=True)

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
            strings={"title": "Klik untuk terbang ke Lokasi Saya", "popup": "Posisi Anda Sekarang!"}
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
            elif menu not in ["KMZ for ATP V2", "KMZ for ATP", "KMZ for ATP V1"]:
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
        st.markdown('</div>', unsafe_allow_html=True)

        # ==============================
        # MINI ANALYTICS & RADAR PLOT
        # ==============================
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown(f'''
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; margin-bottom: 14px;">
            <div style="font-weight: 600; color: #f8fafc; font-size: 0.95rem; display: flex; align-items: center; gap: 8px;">
                <span style="color: #38bdf8;">{SVG_ICONS['chart']}</span>
                <span>Analisis Sektor & Telemetri Jarak</span>
            </div>
            <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #64748b; background: #080c14; padding: 2px 8px; border-radius: 4px; border: 1px solid #1c2638;">
                POLAR RADAR × HAVERSINE
            </span>
        </div>
        ''', unsafe_allow_html=True)

        ana_col1, ana_col2 = st.columns([1, 1.5])

        with ana_col1:
            # Radar Chart for Azimuths
            df_radar = pd.DataFrame({
                'r': [1] * len(df_filtered),
                'theta': df_filtered['Azimuth'].astype(float),
                'Sektor': [f"Sec {i+1}" for i in range(len(df_filtered))]
            })
            fig = px.line_polar(df_radar, r='r', theta='theta', text='Sektor', line_close=True, range_r=[0, 1.4], template='plotly_dark')
            fig.update_traces(
                fill='toself', 
                fillcolor='rgba(2, 132, 199, 0.15)', 
                line=dict(color='#0284c7', width=2), 
                marker=dict(size=6, color='#38bdf8')
            )
            fig.update_layout(
                polar=dict(
                    bgcolor='#080c14',
                    radialaxis=dict(visible=True, range=[0, 1.3], showticklabels=False, linecolor='#1c2638', gridcolor='#1c2638'),
                    angularaxis=dict(direction='clockwise', rotation=90, linecolor='#1c2638', gridcolor='#1c2638', tickfont=dict(color='#94a3b8', size=10, family='JetBrains Mono'))
                ),
                paper_bgcolor='#0d131f',
                plot_bgcolor='#0d131f',
                margin=dict(t=20, b=20, l=20, r=20),
                height=280
            )
            st.plotly_chart(fig, use_container_width=True)

        with ana_col2:
            st.markdown("<div style='font-weight: 600; color: #cbd5e1; font-size: 0.75rem; margin-bottom: 8px; font-family: \"JetBrains Mono\", monospace; text-transform: uppercase; letter-spacing: 0.03em;'>Jarak Titik Uji ke Pusat Site (Haversine Telemetry)</div>", unsafe_allow_html=True)
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

        # Generate KMZ Data
        with st.status('Membangun Berkas Super KMZ...', expanded=True) as status:
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
            import io
            kmz_io = io.BytesIO()
            with zipfile.ZipFile(kmz_io, 'w', zipfile.ZIP_DEFLATED) as z:
                z.write("temp.kml", arcname="doc.kml")

            kmz_data = kmz_io.getvalue()

            if os.path.exists("temp.kml"):
                os.remove("temp.kml")

        def celebration():
            st.balloons()

        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown(f'''
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; margin-bottom: 12px;">
            <div style="font-weight: 600; color: #f8fafc; font-size: 0.92rem; display: flex; align-items: center; gap: 8px;">
                <span style="color: #38bdf8;">{SVG_ICONS['download']}</span>
                <span>Unduh Berkas Hasil Pengolahan</span>
            </div>
            <span class="live-badge"><span class="pulse-dot"></span> ASSETS COMPILED</span>
        </div>
        ''', unsafe_allow_html=True)
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            st.download_button(
                label="Download File KMZ",
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
                label="Download PDF Report",
                data=bytes(pdf_data),
                file_name=f"SSV_Report_{site_id}_{datetime.now().strftime('%d%b%Y')}.pdf",
                mime="application/pdf",
                use_container_width=True,
                type="secondary",
                on_click=celebration
            )

        st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.markdown(
            f'<div class="panel-card" style="text-align: center; padding: 48px 24px; border-style: dashed; border-color: #1c2638; background: #0a0f1a;">'
            f'<div style="display: inline-flex; align-items: center; justify-content: center; width: 48px; height: 48px; border-radius: 10px; background: #121a2b; border: 1px solid #233047; color: #38bdf8; margin-bottom: 14px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">'
            f'{SVG_ICONS["tower"]}'
            f'</div>'
            f'<div style="color: #f8fafc; font-weight: 600; font-size: 1rem; margin-bottom: 4px; letter-spacing: -0.01em;">Awaiting Site Selection</div>'
            f'<p style="color: #64748b; font-size: 0.8125rem; margin: 0 auto; max-width: 440px; line-height: 1.5;">Ketik atau pilih Site ID pada kotak pencarian di atas untuk memvisualisasikan poligon sektor dan mengunduh berkas KMZ.</p>'
            f'</div>',
            unsafe_allow_html=True
        )
