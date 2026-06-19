import streamlit as st
import pandas as pd
import numpy as np
import math
import simplekml
import zipfile
import sys
import os
from datetime import datetime
from shapely.geometry import Polygon
from pyproj import Transformer
import folium
from streamlit_folium import st_folium

# ==============================
# KONFIGURASI WEB
# ==============================
st.set_page_config(page_title="SSV Spot Generator", page_icon="📡", layout="centered")

# Inject Custom CSS for Premium Tool Look
st.markdown("""
<style>
    /* Mengubah warna background dan font agar lebih soft */
    .stApp {
        background-color: #0e1117;
    }
    

    
    h1 {
        text-align: center;
        background: -webkit-linear-gradient(#4facfe, #00f2fe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
        margin-bottom: 5px !important;
        padding-bottom: 0px !important;
    }
    
    .subtitle {
        text-align: center;
        color: #8b949e;
        font-size: 1.1rem;
        margin-bottom: 30px;
    }
    
    /* Tombol utama */
    .stButton>button {
        border-radius: 8px;
        font-weight: bold;
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
        'Ant Height', 'H Beamwidth', 'Power', 'A Gain', 'Freq', 'Band'
    ]
    df_target = pd.DataFrame(columns=kolom_wajib)
    df_target['Site ID Surge'] = df_sumber['Site ID Surge']
    df_target['Site Name Surge'] = df_sumber['Site Name Surge']
    df_target['Longitude'] = pd.to_numeric(df_sumber['Longitude'], errors='coerce')
    df_target['Latitude'] = pd.to_numeric(df_sumber['Latitude'], errors='coerce')

    if 'Azimuth Review' in df_sumber.columns:
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

# ==============================
# HEADER
# ==============================
st.markdown("<h1>📡 SSV Spot Generator</h1>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Pilih Site ID untuk me-render file KMZ Sektoral secara dinamis.</div>", unsafe_allow_html=True)

with st.spinner('Mempersiapkan data...'):
    try:
        df_bersih = load_and_clean_data(SHEET_URL)
    except Exception as e:
        st.error(f"Gagal menarik data: {e}")
        st.stop()

# ==============================
# TOOL KONTROL (CENTERED)
# ==============================


col1, col2 = st.columns([4, 1])
site_list = sorted(df_bersih['Site ID Surge'].unique().tolist())

with col1:
    selected_site = st.selectbox("🔍 Cari Site ID:", site_list, index=None, placeholder="Ketik Site ID di sini...", label_visibility="collapsed")
    
with col2:
    if st.button("🔄 Sync", use_container_width=True, help="Tarik data terbaru dari Google Sheets"):
        st.cache_data.clear()
        st.rerun()



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
    
    # Map Preview dengan tema gelap (CartoDB dark_matter) agar seirama dengan Dark Mode
    m = folium.Map(location=[center_lat, center_lon], zoom_start=16, tiles='CartoDB dark_matter')
    folium.Marker([center_lat, center_lon], popup=site_name, tooltip="Pusat Site", icon=folium.Icon(color='lightgray', icon='info-sign')).add_to(m)
    
    colors = ['#00ff00', '#ff0000', '#ffff00', '#0000ff', '#ff00ff']
    for sec_idx, (_, row) in enumerate(df_filtered.iterrows()):
        lon = float(row['Longitude'])
        lat = float(row['Latitude'])
        az = float(row['Azimuth'])
        bw = float(row['H Beamwidth'])
        
        sector, _, _ = create_sector(lon, lat, az, bw, 400) # Preview radius visual 400m di map web
        coords = [(y, x) for x, y in sector.exterior.coords]
        
        color = colors[sec_idx % len(colors)]
        folium.Polygon(
            locations=coords, color=color, fill=True, fill_opacity=0.3,
            weight=1, tooltip=f"Sektor {sec_idx+1} (Azimuth {az})"
        ).add_to(m)
        
    st_folium(m, height=450, use_container_width=True, returned_objects=[])
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Generate KMZ Button
    if st.button("🚀 Generate KMZ File", use_container_width=True, type="primary"):
        with st.spinner('Merender output KMZ...'):
            kml = simplekml.Kml()
            site_id = selected_site
            folder_site = kml.newfolder(name=f"{site_id} - {site_name}")
            folder_site.visibility = 1

            p_site = folder_site.newpoint(name=f"{site_id} - {site_name}")
            p_site.coords = [(center_lon, center_lat)]
            p_site.style.iconstyle.color = simplekml.Color.white
            p_site.visibility = 1

            folder_ring = folder_site.newfolder(name="RING")
            folder_ring.visibility = 1
            x0, y0 = transformer_to_utm.transform(center_lon, center_lat)

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
            folder_spot = folder_site.newfolder(name="SPOT SSV")
            folder_spot.visibility = 1

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

            kmz_name = f"SSV_{site_id}_{datetime.now().strftime('%d%b%Y')}.kmz"
            kmz_path = os.path.abspath(kmz_name)

            kml.save("temp.kml")
            with zipfile.ZipFile(kmz_path, 'w', zipfile.ZIP_DEFLATED) as z:
                z.write("temp.kml", arcname="doc.kml")

            try:
                if os.name == 'nt':
                    os.startfile(kmz_path)
                elif sys.platform == 'darwin':
                    import subprocess
                    subprocess.call(('open', kmz_path))
                st.success(f"✅ KMZ '{kmz_name}' berhasil dibuat dan otomatis dibuka!")
            except Exception as e:
                pass

            if os.path.exists("temp.kml"):
                os.remove("temp.kml")
                
    st.markdown('</div>', unsafe_allow_html=True)

else:
    st.markdown("""
    <div style="text-align: center; color: #8b949e; margin-top: 50px;">
        <h1 style="font-size: 4rem; opacity: 0.2; background: none; -webkit-text-fill-color: #8b949e;">📡</h1>
        <p>Gunakan kotak pencarian di atas untuk memulai.</p>
    </div>
    """, unsafe_allow_html=True)
