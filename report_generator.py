from fpdf import FPDF
from datetime import datetime
import pandas as pd

class PDFReport(FPDF):
    def header(self):
        self.set_font("Helvetica", 'B', 15)
        self.set_fill_color(30, 27, 75)
        self.set_text_color(255, 255, 255)
        self.cell(0, 15, "SSV Spot Checker - Site Report", border=0, ln=1, align="C", fill=True)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")

def generate_pdf(site_id, site_name, df_sectors, dist_data):
    pdf = PDFReport()
    pdf.add_page()
    
    # Metadata
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(40, 8, "Site ID:")
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 8, str(site_id), ln=True)
    
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(40, 8, "Site Name:")
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 8, str(site_name), ln=True)
    
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(40, 8, "Generated:")
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 8, datetime.now().strftime("%d %b %Y %H:%M:%S"), ln=True)
    
    pdf.ln(10)
    
    # Sector Info
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Sector Configurations", ln=True)
    
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Helvetica", "B", 10)
    
    # Table Header
    pdf.cell(30, 8, "Sector", border=1, fill=True)
    pdf.cell(30, 8, "Azimuth", border=1, fill=True)
    pdf.cell(80, 8, "Cell Name", border=1, fill=True)
    pdf.cell(30, 8, "PCI", border=1, fill=True, ln=True)
    
    pdf.set_font("Helvetica", "", 10)
    for idx, row in df_sectors.iterrows():
        pdf.cell(30, 8, f"Sektor {idx+1}", border=1)
        pdf.cell(30, 8, str(row.get('Azimuth', '-')), border=1)
        pdf.cell(80, 8, str(row.get('Cell Name', '-')), border=1)
        pdf.cell(30, 8, str(row.get('PCI', '-')), border=1, ln=True)
        
    pdf.ln(10)
    
    # Field Test Spots
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Field Test Spots", ln=True)
    
    if not dist_data:
        pdf.set_font("Helvetica", "", 12)
        pdf.cell(0, 10, "No field test spots available.", ln=True)
    else:
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(120, 8, "Spot Name", border=1, fill=True)
        pdf.cell(50, 8, "Haversine Distance", border=1, fill=True, ln=True)
        
        pdf.set_font("Helvetica", "", 10)
        for spot in dist_data:
            pdf.cell(120, 8, str(spot['Titik Tes']), border=1)
            pdf.cell(50, 8, str(spot['Jarak Aktual (m)']), border=1, ln=True)

    # Output to bytes
    return bytes(pdf.output())
