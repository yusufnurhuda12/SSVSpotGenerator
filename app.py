import os
import csv
import io
import math
import time
from flask import Flask, render_template, request, send_file
import simplekml
import pandas as pd
import numpy as np
from pyproj import Transformer

# Explicitly define template folder path for Vercel Serverless
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
app = Flask(__name__, template_folder=template_dir)

@app.route('/')
def index():
    return render_template('index.html')

import tempfile
import folium

SHEET_URL = "https://docs.google.com/spreadsheets/d/1Yscupy_kQJzFBLOv_2lS0u2J-fKi5XqFoCyjRFXDlLA/export?format=csv&gid=118124849"

_sheet_cache = None
_sheet_cache_time = 0

def get_sheet_data():
    global _sheet_cache, _sheet_cache_time
    if _sheet_cache is None or time.time() - _sheet_cache_time > 600:
        try:
            _sheet_cache = pd.read_csv(SHEET_URL)
            _sheet_cache.columns = _sheet_cache.columns.str.replace('\\n', ' ', regex=False).str.replace(' +', ' ', regex=True).str.strip()
            _sheet_cache_time = time.time()
        except Exception as e:
            print("Failed to fetch sheet:", e)
            return None
    return _sheet_cache

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
    return pts_latlon


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

    import csv
    import io
    # Gunakan csv.reader asli bawaan Python yang pintar meng-handle multiline cell dari Excel
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
        # Search backwards to find lat/lon, usually at the end
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

    # Determine headers
    num_cols = len(rows[data_start])
    header_row = rows[data_start - 1] if data_start > 0 else []
    
    headers = []
    if len(header_row) >= num_cols:
        headers = header_row[-num_cols:]
    else:
        # Pad on the left
        pad_len = num_cols - len(header_row)
        headers = [f"Column {i+1}" for i in range(pad_len)] + header_row
        
    # Clean headers
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
            
            # Carry forward values for the first few columns
            # We assume columns before the Sector column (usually index 3) are merged
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
        
        # Try to find Sector
        sector_val = ""
        for i, h in enumerate(headers):
            if 'sector' in h.lower():
                sector_val = row_data.get(h, '').strip()
                break
        
        # If header for sector wasn't found, try heuristic: column 3 is usually sector
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
            'desc_html': desc_html
        })
        
    return points, None, 200

@app.route('/generate', methods=['POST'])
def generate():
    text_data = request.form.get('data', '')
    points, error_msg, status_code = parse_input_data(text_data)
    
    if error_msg:
        return error_msg, status_code

    kml = simplekml.Kml()
    for pt in points:
        pnt = kml.newpoint(name=pt['name'], coords=[(pt['lon'], pt['lat'])])
        pnt.description = pt['desc_html']
        pnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/pushpin/red-pushpin.png'

    temp_dir = tempfile.gettempdir()
    kmz_path = os.path.join(temp_dir, "output.kmz")
    kml.savekmz(kmz_path)
    
    return send_file(
        kmz_path,
        as_attachment=True,
        download_name='pinpoints.kmz',
        mimetype='application/vnd.google-earth.kmz'
    )

@app.route('/preview', methods=['POST'])
def preview():
    text_data = request.form.get('data', '')
    site_id = request.form.get('site_id', '').strip()
    
    points, error_msg, status_code = [], None, 200
    if text_data.strip():
        points_result = parse_input_data(text_data)
        if points_result:
            points, error_msg, status_code = points_result
    
    if error_msg and not site_id:
        return error_msg, status_code
        
    m = None
    center_lat, center_lon = 0, 0
    
    if site_id:
        df_all = get_sheet_data()
        if df_all is not None:
            df_site = df_all[df_all['Site ID Surge'] == site_id].copy()
            if not df_site.empty:
                df_site['Longitude'] = pd.to_numeric(df_site['Longitude'], errors='coerce')
                df_site['Latitude'] = pd.to_numeric(df_site['Latitude'], errors='coerce')
                
                if 'Azimuth Review' in df_site.columns:
                    az_review = pd.to_numeric(df_site['Azimuth Review'], errors='coerce')
                    az_biasa = pd.to_numeric(df_site['Azimuth'], errors='coerce')
                    has_review = az_review.notna().any()
                    df_site['Azimuth'] = np.where(has_review, az_review, az_biasa)
                else:
                    df_site['Azimuth'] = pd.to_numeric(df_site['Azimuth'], errors='coerce')
                
                kondisi_terbalik = (df_site['Longitude'].abs() < 20) & (df_site['Latitude'].abs() > 80)
                temp_lon = df_site.loc[kondisi_terbalik, 'Longitude']
                df_site.loc[kondisi_terbalik, 'Longitude'] = df_site.loc[kondisi_terbalik, 'Latitude']
                df_site.loc[kondisi_terbalik, 'Latitude'] = temp_lon

                df_site['Longitude'] = df_site.groupby('Site ID Surge')['Longitude'].transform(lambda x: x.ffill().bfill())
                df_site['Latitude'] = df_site.groupby('Site ID Surge')['Latitude'].transform(lambda x: x.ffill().bfill())

                df_site['H Beamwidth'] = 120
                df_site = df_site.dropna(subset=['Longitude', 'Latitude', 'Azimuth'])
                
                if not df_site.empty:
                    center_lon = float(df_site.iloc[0]['Longitude'])
                    center_lat = float(df_site.iloc[0]['Latitude'])
                    site_name = df_site.iloc[0]['Site Name Surge']
                    
                    m = folium.Map(location=[center_lat, center_lon], zoom_start=16, tiles='CartoDB dark_matter')
                    folium.Marker([center_lat, center_lon], popup=site_name, tooltip="Pusat Site", icon=folium.Icon(color='lightgray', icon='info-sign')).add_to(m)
                    
                    colors = ['#00ff00', '#ff0000', '#ffff00', '#0000ff', '#ff00ff']
                    for sec_idx, (_, row) in enumerate(df_site.iterrows()):
                        lon = float(row['Longitude'])
                        lat = float(row['Latitude'])
                        az = float(row['Azimuth'])
                        bw = float(row['H Beamwidth'])
                        
                        sector_pts = create_sector(lon, lat, az, bw, 500)
                        coords = [(y, x) for x, y in sector_pts]
                        
                        color = colors[sec_idx % len(colors)]
                        folium.Polygon(
                            locations=coords, color=color, fill=True, fill_opacity=0.3,
                            weight=1, tooltip=f"Sektor {sec_idx+1} (Azimuth {int(az)})"
                        ).add_to(m)
    
    if m is None:
        if points:
            avg_lat = sum(p['lat'] for p in points) / len(points)
            avg_lon = sum(p['lon'] for p in points) / len(points)
            m = folium.Map(location=[avg_lat, avg_lon], zoom_start=16, tiles='CartoDB dark_matter')
        else:
            return "No valid coordinates found in the data and no valid Site ID provided.", 400
            
    if points:
        for pt in points:
            folium.Marker(
                location=[pt['lat'], pt['lon']],
                popup=folium.Popup(pt['desc_html'], max_width=300),
                tooltip=pt['name'],
                icon=folium.Icon(color='red', icon='info-sign')
            ).add_to(m)
            
    return m.get_root().render()

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
