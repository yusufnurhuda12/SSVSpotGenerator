import os
import io
import zipfile
import urllib.request
import gdown
import streamlit as st

FOLDER_ID = "1tiQ7lT0bUYEw8lwzzryPwKhxadq8pqKu"
DRIVE_FOLDER_URL = f"https://drive.google.com/drive/folders/{FOLDER_ID}"

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_gdrive_tilting_files(folder_id=FOLDER_ID):
    """
    Fetch all files from Google Drive folder using gdown folder crawler.
    Discovers all 540+ files with pagination automatically.
    """
    files_dict = {}
    try:
        gdrive_items = gdown.download_folder(id=folder_id, skip_download=True, quiet=True)
        for item in gdrive_items:
            fname = item.path.replace("\\", "/").split("/")[-1].strip()
            if not fname or "." not in fname:
                continue
            site_id_raw = fname.rsplit(".", 1)[0].strip()
            mime = "image/jpeg"
            if fname.lower().endswith(".png"):
                mime = "image/png"
            elif fname.lower().endswith(".webp"):
                mime = "image/webp"
            elif fname.lower().endswith(".pdf"):
                mime = "application/pdf"
                
            files_dict[fname] = {
                "id": item.id,
                "filename": fname,
                "mime": mime,
                "site_id": site_id_raw,
                "view_url": f"https://drive.google.com/file/d/{item.id}/view?usp=sharing",
                "download_url": f"https://drive.google.com/uc?export=download&id={item.id}",
                "thumbnail_url": f"https://lh3.googleusercontent.com/d/{item.id}"
            }
    except Exception as e:
        print(f"Error in fetch_gdrive_tilting_files: {e}")
        
    return files_dict

def find_tilting_photos_for_site(site_id, tilting_files):
    """
    Search and match tilting photos in tilting_files dictionary for a given Site ID.
    Handles exact match, case-insensitivity, and revision suffixes (e.g., _R01, _NEW).
    """
    if not site_id:
        return []
    
    clean_site_id = str(site_id).strip().upper()
    exact_matches = []
    suffix_matches = []
    partial_matches = []
    
    for filename, info in tilting_files.items():
        file_site = info["site_id"].strip().upper()
        if file_site == clean_site_id:
            exact_matches.append(info)
        elif file_site.startswith(clean_site_id + "_") or clean_site_id.startswith(file_site + "_"):
            suffix_matches.append(info)
        elif clean_site_id in file_site:
            partial_matches.append(info)
            
    all_res = exact_matches + suffix_matches + partial_matches
    seen = set()
    deduped = []
    for item in all_res:
        if item["filename"] not in seen:
            seen.add(item["filename"])
            deduped.append(item)
            
    return deduped

@st.cache_data(ttl=3600, show_spinner=False)
def download_image_bytes(file_id):
    """
    Download image binary from Google Drive with caching.
    """
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read()

def create_tilting_zip(file_items):
    """
    Download and pack multiple tilting photos into a single ZIP archive bytes.
    """
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for item in file_items:
            try:
                img_data = download_image_bytes(item["id"])
                zip_file.writestr(item["filename"], img_data)
            except Exception as e:
                print(f"Error packing {item['filename']} to zip: {e}")
    return zip_buffer.getvalue()
