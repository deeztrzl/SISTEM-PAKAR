# Sistem Pakar Diagnosa Medis

## Deskripsi Proyek

Sistem pakar untuk diagnosa medis yang menggunakan **forward chaining** dengan **certainty factor (CF)** untuk melakukan inferensi. Sistem ini mampu menangani aturan sekuensial dan paralel sesuai dengan persyaratan tugas SISPAK 2.

## Tim Pengembang
- **Tim**: SISPAK 2
- **Versi**: 1.0
- **Tanggal**: Oktober 2025

## Fitur Utama

### ✅ Forward Chaining Inference Engine
- Implementasi algoritma forward chaining yang lengkap
- Mendukung inferensi bertingkat dari gejala ke diagnosa
- Tracking aturan yang telah dieksekusi

### ✅ Certainty Factor (CF) Calculations
- Formula penggabungan CF untuk aturan paralel: `CF = CF1 + CF2 - (CF1 × CF2)`
- Perhitungan CF untuk aturan sekuensial: `CF = min(CF_premises) × CF_rule`
- Normalisasi CF dalam rentang 0.0 - 1.0

### ✅ Sequential & Parallel Rules Support
- **Aturan Sekuensial**: Aturan yang menggunakan hasil aturan lain sebagai premis
- **Aturan Paralel**: Dua atau lebih aturan menghasilkan kesimpulan sama dengan CF berbeda

### ✅ User Interface
- **Web Interface**: Modern responsive web application menggunakan Flask
- **Desktop GUI**: Interface grafis menggunakan tkinter  
- **CLI**: Command line interface untuk testing
- Input gejala dengan tingkat keyakinan
- Tampilan hasil diagnosa yang terstruktur
- Real-time diagnosis dengan AJAX
- Responsive design untuk mobile dan desktop

### ✅ Knowledge Base
- File `rules.json` berisi 15 aturan medis
- Cakupan: infeksi, pneumonia, gastroenteritis, komplikasi
- Aturan berdasarkan literatur medis yang valid

## Struktur Proyek

```
medical_expert_system/
│
├── rules.json                     # Knowledge base (basis pengetahuan)
├── gui.py                         # Desktop GUI aplikasi
├── cli.py                         # Command line interface
├── launcher.py                    # Launcher untuk semua interface
├── README.md                      # Dokumentasi ini
│
├── web_ui/                        # Web Interface (Flask)
│   ├── app.py                     # Flask web server
│   ├── static/                    # CSS, JS, images
│   │   ├── css/style.css
│   │   └── js/diagnosis.js
│   └── templates/                 # HTML templates
│       ├── base.html
│       ├── index.html
│       ├── diagnosis.html
│       ├── rules.html
│       ├── about.html
│       └── error.html
│
├── inference_engine/              # Mesin inferensi
│   ├── __init__.py
│   └── forward_chaining.py        # Implementasi forward chaining
│
└── ui/                           # User interface
    ├── __init__.py
    └── gui.py                    # GUI menggunakan tkinter
```

## Basis Pengetahuan (Knowledge Base)

### Struktur Rules.json

```json
[
  {
    "id": "R1",
    "if": ["demam_tinggi", "sakit_kepala"],
    "then": "suspek_infeksi",
    "cf": 0.7,
    "description": "Demam tinggi dan sakit kepala mengindikasikan suspek infeksi"
  }
]
```

### Jenis Aturan

#### 1. Aturan Sekuensial
Aturan yang menggunakan hasil dari aturan lain sebagai premis:

- **R4**: `suspek_infeksi + leukositosis → infeksi_bakteri`
- **R5**: `suspek_infeksi_paru + infiltrat_paru → pneumonia` 
- **R8**: `infeksi_bakteri + tidak_responsif_antibiotik → resistensi_antibiotik`
- **R9**: `pneumonia + gagal_napas → pneumonia_berat`

#### 2. Aturan Paralel
Aturan yang menghasilkan kesimpulan sama dengan CF berbeda:

- **R5 & R6**: Keduanya menghasilkan `pneumonia` dengan CF berbeda
- **R4 & R11**: Menghasilkan kesimpulan berbeda dari `suspek_infeksi`
- **R12 & R13**: Keduanya menghasilkan `komplikasi_serius`

### Domain Pengetahuan

Sistem ini mencakup diagnosa untuk:
- **Infeksi**: Bakteri, viral, suspek infeksi
- **Penyakit Paru**: Pneumonia, pneumonia berat
- **Gastroenteritis**: Ringan hingga berat
- **Komplikasi**: Resistensi antibiotik, komplikasi serius

## Instalasi dan Penggunaan

### Persyaratan Sistem
- **Python 3.7+** (tested on Python 3.11)
- **Flask 2.0+** untuk web interface
- **Flask-CORS** untuk CORS handling
- **pytest** untuk testing
- **tkinter** (biasanya sudah terinstall dengan Python)

### Install Dependencies
```bash
pip install flask flask-cors pytest
```
- Sistem operasi: Windows, Linux, atau macOS

### Cara Menjalankan

#### 1. Web Interface (Recommended)
```bash
cd medical_expert_system/web_ui
python app.py
```
Akses melalui browser di: http://localhost:5000

#### 2. Desktop GUI
```bash
cd medical_expert_system
python gui.py
```

#### 3. CLI Mode (Command Line)
```bash
cd medical_expert_system
python cli.py
```

#### 4. Launcher (Semua Mode)
```bash
cd medical_expert_system
python launcher.py
```

#### 5. Testing
```bash
cd medical_expert_system
python -m pytest tests/ -v
```

### Panduan Penggunaan GUI

1. **Input Gejala**:
   - Centang gejala yang dialami pasien
   - Atur certainty factor (0.1 - 1.0) untuk setiap gejala
   - Semakin tinggi CF, semakin yakin terhadap gejala tersebut

2. **Proses Diagnosa**:
   - Klik tombol "DIAGNOSA" untuk memulai inferensi
   - Sistem akan menjalankan forward chaining
   - Hasil akan ditampilkan di panel kanan

3. **Interpretasi Hasil**:
   - **CF 0.8-1.0**: Keyakinan Sangat Tinggi
   - **CF 0.6-0.8**: Keyakinan Tinggi  
   - **CF 0.4-0.6**: Keyakinan Sedang
   - **CF 0.1-0.4**: Keyakinan Rendah

4. **Jejak Inferensi**:
   - Klik "Tampilkan Jejak Inferensi" untuk melihat proses reasoning
   - Berguna untuk memahami bagaimana sistem mencapai kesimpulan

## Contoh Penggunaan

### Skenario 1: Pneumonia
**Input**:
- `demam_tinggi` (CF: 0.9)
- `batuk_produktif` (CF: 0.8)
- `nyeri_dada` (CF: 0.7)

**Proses Inferensi**:
1. Rule R6 diaktifkan → `pneumonia` (CF: 0.56)
2. Jika ditambah `infiltrat_paru` (CF: 0.8)
3. Rule R1 → `suspek_infeksi` (CF: 0.63)
4. Rule R5 → `pneumonia` (CF: 0.504)
5. **Penggabungan CF**: 0.56 + 0.504 - (0.56 × 0.504) = 0.782

**Output**: `pneumonia` dengan CF: 0.782 (Keyakinan Tinggi)

### Skenario 2: Infeksi Bakteri (Sekuensial)
**Input**:
- `demam_tinggi` (CF: 0.8)
- `sakit_kepala` (CF: 0.7)  
- `leukositosis` (CF: 0.9)

**Proses Inferensi**:
1. Rule R1: `demam_tinggi + sakit_kepala → suspek_infeksi` (CF: 0.49)
2. Rule R4: `suspek_infeksi + leukositosis → infeksi_bakteri` (CF: 0.416)

**Output**: `infeksi_bakteri` dengan CF: 0.416 (Keyakinan Sedang)

## Algoritma Forward Chaining

### Pseudocode
```
1. Inisialisasi facts dengan input gejala
2. WHILE ada perubahan DO
   3. FOR setiap rule DO
      4. IF semua premis rule ada di facts THEN
         5. Hitung CF_rule = min(CF_premises) × CF_rule
         6. IF kesimpulan sudah ada (aturan paralel) THEN
            7. CF_new = CF_old + CF_rule - (CF_old × CF_rule)
         8. ELSE (aturan sekuensial)
            9. Tambahkan kesimpulan baru ke facts
         10. Tandai rule sebagai fired
11. Return facts
```

### Kompleksitas
- **Time Complexity**: O(n × m × k) 
  - n = jumlah iterasi
  - m = jumlah rules  
  - k = rata-rata premis per rule
- **Space Complexity**: O(f + r)
  - f = jumlah facts
  - r = jumlah rules

## Certainty Factor Formulas

### 1. Untuk Aturan Sekuensial
```
CF(rule) = min(CF(premise1), CF(premise2), ...) × CF(rule)
```

### 2. Untuk Aturan Paralel
```
CF(combined) = CF1 + CF2 - (CF1 × CF2)
```

Dimana:
- CF1 = certainty factor kesimpulan yang sudah ada
- CF2 = certainty factor dari rule baru
- Hasil selalu ≤ 1.0

## Validasi dan Testing

### Test Cases
1. **Single Rule**: Input gejala yang mengaktifkan satu rule
2. **Sequential Rules**: Rantai inferensi gejala → diagnosa → komplikasi  
3. **Parallel Rules**: Multiple rules menghasilkan kesimpulan sama
4. **Edge Cases**: CF ekstrem (0.1, 1.0), gejala tidak valid

### Expected Behavior
- CF hasil tidak boleh > 1.0
- Rules hanya fire sekali per sesi
- Aturan sekuensial menunggu premis tersedia
- Penggabungan CF untuk aturan paralel

## Referensi dan Literatur

### Sumber Utama
1. **Sistem Pakar**: Turban, E. & Aronson, J. (2001). Decision Support Systems and Intelligent Systems
2. **Forward Chaining**: Russell, S. & Norvig, P. (2020). Artificial Intelligence: A Modern Approach
3. **Certainty Factor**: Shortliffe, E.H. & Buchanan, B.G. (1975). A model of inexact reasoning in medicine

### Referensi Medis
1. **Pneumonia**: WHO Guidelines for Pneumonia Diagnosis (2019)
2. **Infeksi**: CDC Guidelines for Infection Control (2020)
3. **Gastroenteritis**: Mayo Clinic Medical Reference (2021)

### Modifikasi dari Literatur Asli
Untuk memenuhi persyaratan aturan sekuensial dan paralel, kami melakukan modifikasi:

1. **Penambahan Rules Sekuensial**: 
   - R4, R5, R8, R9, R12, R14, R15 dibuat sebagai aturan sekuensial
   - Menggunakan output dari aturan sebelumnya sebagai input

2. **Penambahan Rules Paralel**:
   - R5 & R6 untuk pneumonia
   - R4 & R11 untuk jenis infeksi
   - R12 & R13 untuk komplikasi serius

3. **Justifikasi Medis**:
   - Semua modifikasi berdasarkan logical medical reasoning
   - Konsisten dengan practice guidelines yang ada
   - Maintained clinical validity

## Kesimpulan

Sistem pakar ini berhasil mengimplementasikan:
- ✅ Forward chaining yang robust
- ✅ Certainty factor calculations yang akurat  
- ✅ Support untuk aturan sekuensial dan paralel
- ✅ User interface yang user-friendly
- ✅ Knowledge base yang komprehensif

Sistem dapat digunakan sebagai **decision support tool** untuk diagnosa medis dengan tingkat akurasi yang baik, khususnya untuk kasus-kasus infeksi dan komplikasinya.

---

**Catatan**: Sistem ini dirancang untuk tujuan edukatif dan penelitian. Untuk penggunaan klinis, diperlukan validasi lebih lanjut dengan data real dan konsultasi dengan ahli medis.