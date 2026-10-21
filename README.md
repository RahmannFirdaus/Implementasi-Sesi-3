# 🗺️ GIS Asset Management Processor

> **Automasi Pengolahan & Integrasi Data Aset Infrastruktur Publik**  

---

## 📖 Deskripsi

**GIS Asset Management Processor** adalah script Python yang dirancang untuk mengotomasi alur kerja pengolahan data aset infrastruktur publik berbasis geospasial. Script ini mengimplementasikan pipeline lengkap mulai dari pembacaan data mentah survey lapangan, validasi koordinat, penghitungan skor prioritas penanganan, hingga konversi ke format **GeoJSON** yang siap diimpor ke platform GIS seperti **QGIS**, **PostGIS**, maupun **WebGIS**.

> 💡 Inspirasi materi: **Widi Primadepa** (City Care Property NZ / Open-Source GIS Workflow)

---

## 📁 Struktur Repositori

```
Sesi 3/
├── gis_asset_processor.py      # Script utama pemrosesan data GIS
├── asset_inspection.geojson    # Output GeoJSON hasil konversi data sampel
└── README.md                   # Dokumentasi proyek
```

---

## ⚙️ Fitur Utama

| Fitur | Deskripsi |
|---|---|
| 📂 **Multi-format Input** | Mendukung pembacaan data survey dari file `.json` dan `.csv` |
| ✅ **Validasi Koordinat** | Validasi otomatis koordinat WGS84 (Lat: -90°~+90°, Lon: -180°~+180°) |
| 📊 **Skor Prioritas** | Kalkulasi skor penanganan aset (skala 1–100) berdasarkan tingkat keparahan & jenis aset |
| 🗺️ **Ekspor GeoJSON** | Konversi data ke format GeoJSON standar (RFC 7946 / OGC CRS84) |
| 📋 **Laporan Ringkasan** | Menghasilkan statistik eksekutif distribusi kategori & aset prioritas tinggi |

---

## 🚀 Cara Menjalankan

### Prasyarat

- Python **3.7+**
- Tidak membutuhkan library eksternal (hanya menggunakan modul bawaan Python)

### Menjalankan Script

```bash
python gis_asset_processor.py
```

### Contoh Output

```
=== GIS Asset Processor (Demo Run) ===
✅ Sukses mengkonversi 3 fitur spasial ke: asset_inspection.geojson
📊 Ringkasan Statistik Laporan:
   - Total Laporan: 3
   - Prioritas Tinggi (Score >= 60): 2
   - Distribusi Kategori: {'pohon_tumbuh': 1, 'jalan_rusak': 1, 'penerangan_jalan': 1}
```

---

## 🔧 Penjelasan Fungsi

### `load_raw_survey_data(filepath)`
Membaca data mentah hasil survey dari file `.json` atau `.csv`.  
Akan melempar `FileNotFoundError` jika file tidak ditemukan, dan `ValueError` jika format file tidak didukung.

### `validate_coordinates(lat, lon)`
Memvalidasi pasangan koordinat geospasial dalam sistem referensi **WGS84**.  
Mengembalikan `(None, None)` jika koordinat tidak valid atau berada di luar rentang yang diizinkan.

### `calculate_priority_score(severity, asset_type)`
Menghitung skor prioritas penanganan aset dengan rumus:

```
Skor = (Bobot Keparahan × 20) × Bobot Jenis Aset
```

**Bobot Tingkat Keparahan:**
| Level | Bobot |
|---|---|
| `low` | 1 |
| `medium` | 2 |
| `high` | 3 |
| `critical` | 4 |

**Bobot Jenis Aset:**
| Jenis Aset | Bobot |
|---|---|
| `jalan_rusak` | 1.5 |
| `drainase_tumpat` | 1.4 |
| `pohon_tumbuh` | 1.3 |
| `penerangan_jalan` | 1.2 |
| `fasilitas_umum` | 1.0 |

### `convert_to_geojson(data_list, output_geojson_path)`
Mengkonversi list data aset terproses menjadi file **GeoJSON FeatureCollection** standar.  
Aset dengan koordinat tidak valid akan dilewati secara otomatis.

### `generate_summary_report(data_list)`
Menghasilkan statistik ringkasan meliputi total laporan, distribusi per kategori aset, dan jumlah aset dengan skor prioritas ≥ 60 (prioritas tinggi).

---

## 📄 Format Data Output (GeoJSON)

File `asset_inspection.geojson` menggunakan standar **GeoJSON FeatureCollection** dengan sistem koordinat referensi **OGC CRS84 (WGS84)**:

```json
{
  "type": "FeatureCollection",
  "name": "Public_Asset_Inspection_Data",
  "crs": {
    "type": "name",
    "properties": { "name": "urn:ogc:def:crs:OGC:1.3:CRS84" }
  },
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [102.2608, -3.7928]
      },
      "properties": {
        "asset_id": "AST-001",
        "asset_name": "Pohon Rindang Rawan Tumbang",
        "asset_type": "pohon_tumbuh",
        "severity": "critical",
        "priority_score": 100.0,
        "status": "reported",
        "reporter_notes": "...",
        "report_date": "2026-10-18"
      }
    }
  ]
}
```

---

## 🗂️ Data Sampel (Demo)

Script ini dilengkapi dengan 3 data sampel hasil simulasi survey lapangan di area **Bengkulu**:

| ID | Nama Aset | Tipe | Keparahan | Skor Prioritas |
|---|---|---|---|---|
| AST-001 | Pohon Rindang Rawan Tumbang | `pohon_tumbuh` | Critical | **100.0** |
| AST-002 | Jalan Berlubang Parah | `jalan_rusak` | High | **90.0** |
| AST-003 | Lampu PJU Padam | `penerangan_jalan` | Medium | **48.0** |

---

## 🔗 Integrasi dengan Platform GIS

File `.geojson` yang dihasilkan dapat langsung digunakan di:

- **[QGIS](https://qgis.org/)** — Drag & drop file `.geojson` ke layer panel
- **[PostGIS](https://postgis.net/)** — Import menggunakan `ogr2ogr` atau `shp2pgsql`
- **[Leaflet.js](https://leafletjs.com/)** / **[Mapbox](https://www.mapbox.com/)** — Load via `fetch()` atau API layer
- **[geojson.io](https://geojson.io/)** — Preview online langsung di browser
