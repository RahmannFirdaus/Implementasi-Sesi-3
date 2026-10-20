"""
GIS Asset Management Processor
------------------------------
Studi Kasus: Automasi Pengolahan & Integrasi Data Aset Infrastruktur Publik
Inspirasi Materi: Widi Primadepa (City Care Property NZ / Open-Source GIS Workflow)

Deskripsi:
Script ini membaca data mentah hasil survey/pelaporan aset (CSV/JSON),
melakukan validasi koordinat spasial, menghitung skor prioritas perbaikan,
mengkonversi data ke format GeoJSON (siap diimpor ke QGIS/PostGIS/WebGIS),
serta memproduksi ringkasan eksekutif status aset.
"""

import json
import csv
from datetime import datetime
import os

def load_raw_survey_data(filepath):
    """Membaca data mentah hasil survey dari file JSON atau CSV."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File data tidak ditemukan: {filepath}")
        
    with open(filepath, 'r', encoding='utf-8') as f:
        if filepath.endswith('.json'):
            return json.load(f)
        elif filepath.endswith('.csv'):
            reader = csv.DictReader(f)
            return list(reader)
        else:
            raise ValueError("Format file harus .json atau .csv")

def validate_coordinates(lat, lon):
    """Validasi koordinat geospasial WGS84 (Lat: -90 s/d 90, Lon: -180 s/d 180)."""
    try:
        lat = float(lat)
        lon = float(lon)
        if -90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0:
            return lat, lon
        return None, None
    except (ValueError, TypeError):
        return None, None

def calculate_priority_score(severity, asset_type):
    """
    Menghitung skor prioritas penanganan aset (skala 1-100).
    Tingkat Keparahan: Low (1), Medium (2), High (3), Critical (4)
    Bobot Jenis Aset: Jalan Rusak (1.5), Drainase Tumpat (1.4), Pohon (1.3), PJU (1.2)
    """
    severity_weights = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
    type_weights = {
        'pohon_tumbuh': 1.3,
        'jalan_rusak': 1.5,
        'penerangan_jalan': 1.2,
        'drainase_tumpat': 1.4,
        'fasilitas_umum': 1.0
    }
    
    sev_score = severity_weights.get(str(severity).lower(), 1)
    type_weight = type_weights.get(str(asset_type).lower(), 1.0)
    
    raw_score = (sev_score * 20) * type_weight
    return min(round(raw_score, 1), 100.0)

def convert_to_geojson(data_list, output_geojson_path):
    """Mengkonversi list aset terproses menjadi GeoJSON FeatureCollection."""
    features = []
    
    for item in data_list:
        lat, lon = validate_coordinates(item.get('latitude'), item.get('longitude'))
        if lat is None or lon is None:
            continue  # Dilewati jika koordinat tidak valid
            
        priority = calculate_priority_score(item.get('severity', 'low'), item.get('asset_type', 'fasilitas_umum'))
        
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [lon, lat]  # Format GeoJSON: [Longitude, Latitude]
            },
            "properties": {
                "asset_id": item.get('asset_id'),
                "asset_name": item.get('asset_name'),
                "asset_type": item.get('asset_type'),
                "severity": item.get('severity'),
                "priority_score": priority,
                "status": item.get('status', 'reported'),
                "reporter_notes": item.get('notes', ''),
                "report_date": item.get('report_date', datetime.now().strftime('%Y-%m-%d'))
            }
        }
        features.append(feature)
        
    geojson_data = {
        "type": "FeatureCollection",
        "name": "Public_Asset_Inspection_Data",
        "crs": {
            "type": "name",
            "properties": {
                "name": "urn:ogc:def:crs:OGC:1.3:CRS84"
            }
        },
        "features": features
    }
    
    with open(output_geojson_path, 'w', encoding='utf-8') as f:
        json.dump(geojson_data, f, indent=2, ensure_ascii=False)
        
    return len(features)

def generate_summary_report(data_list):
    """Menghasilkan statistik ringkasan aset yang perlu tindakan penanganan."""
    summary = {
        "total_reports": len(data_list),
        "by_category": {},
        "high_priority_count": 0
    }
    
    for item in data_list:
        atype = item.get('asset_type', 'lainnya')
        summary['by_category'][atype] = summary['by_category'].get(atype, 0) + 1
        
        score = calculate_priority_score(item.get('severity', 'low'), atype)
        if score >= 60.0:
            summary['high_priority_count'] += 1
            
    return summary

# --- EKSEKUSI DEMO/UJI COBA SCRIPT ---
if __name__ == "__main__":
    print("=== GIS Asset Processor (Demo Run) ===")
    
    # Data sampel simulasi hasil survey lapangan
    sample_reports = [
        {
            "asset_id": "AST-001",
            "asset_name": "Pohon Rindang Rawan Tumbang",
            "asset_type": "pohon_tumbuh",
            "latitude": -3.7928,
            "longitude": 102.2608,
            "severity": "critical",
            "notes": "Dahan pohon lapuk menutupi kabel listrik di Jalan Unib Depan",
            "report_date": "2026-10-18"
        },
        {
            "asset_id": "AST-002",
            "asset_name": "Jalan Berlubang Parah",
            "asset_type": "jalan_rusak",
            "latitude": -3.8011,
            "longitude": 102.2715,
            "severity": "high",
            "notes": "Lubang jalan kedalaman 15cm membahayakan pengendara motor",
            "report_date": "2026-10-19"
        },
        {
            "asset_id": "AST-003",
            "asset_name": "Lampu PJU Padam",
            "asset_type": "penerangan_jalan",
            "latitude": -3.7850,
            "longitude": 102.2543,
            "severity": "medium",
            "notes": "Lampu jalan mati di tikungan dekat kampus",
            "report_date": "2026-10-19"
        }
    ]
    
    out_file = "asset_inspection.geojson"
    count = convert_to_geojson(sample_reports, out_file)
    stats = generate_summary_report(sample_reports)
    
    print(f"✅ Sukses mengkonversi {count} fitur spasial ke: {out_file}")
    print("📊 Ringkasan Statistik Laporan:")
    print(f"   - Total Laporan: {stats['total_reports']}")
    print(f"   - Prioritas Tinggi (Score >= 60): {stats['high_priority_count']}")
    print(f"   - Distribusi Kategori: {stats['by_category']}")
