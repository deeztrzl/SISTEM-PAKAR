# Sistem Pakar Diagnosa Kerusakan Sepeda Motor Matic

## Deskripsi
Web App Sistem Pakar untuk mendiagnosa kerusakan sepeda motor matic menggunakan metode Forward Chaining dengan Certainty Factor (CF).

## Fitur
- Forward Chaining Algorithm dengan Fallback Mechanism
- Certainty Factor calculation
- Aturan sekuensial dan paralel
- Web interface dengan accordion kategorisasi gejala
- Hasil diagnosis dengan tingkat kepercayaan
- Partial matching untuk gejala yang tidak exact match
- Sistem TIDAK PERNAH mengembalikan "Tidak ada diagnosis"

## Teknologi
- Backend: Python Flask
- Frontend: HTML, CSS, JavaScript, Bootstrap 5
- Knowledge Base: JSON

## Basis Pengetahuan
- 34 Gejala (K01-K34) dalam 8 kategori
- 11 Jenis Kerusakan (A01-A11)
- 25 Rules dengan Certainty Factor
- 3 Rules sekuensial, 19 rules paralel

## Instalasi & Menjalankan
```bash
pip install flask
python app.py
```

Akses aplikasi di: http://localhost:5000

## Struktur Project
```
motorcycle_expert_system/
├── app.py                          # Flask web application
├── rules.json                      # Knowledge base rules + CF
├── symptoms.json                   # Daftar gejala K01-K34
├── symptoms_categorized.json       # Gejala dikategorikan untuk UI
├── damages.json                    # Daftar kerusakan A01-A11
├── inference_engine/
│   └── engine.py                   # Forward chaining + CF engine
├── templates/
│   └── index.html                  # Main page dengan accordion
├── requirements.txt                # Python dependencies
└── README.md                       # Dokumentasi project
```


## Pengembang
Berdasarkan jurnal: "Development of a Mobile Expert System for the Diagnosis on Motorcycle Damage Using Forward Chaining Algorithm"

Dikembangkan dengan improvements:
- ✅ Certainty Factor (CF) 
- ✅ Aturan sekuensial/paralel
- ✅ Fallback diagnosis mechanism
- ✅ Accordion UI categorization