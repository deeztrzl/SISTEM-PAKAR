#!/usr/bin/env python3
"""
Sistem Pakar Diagnosa Medis
===========================

Aplikasi sistem pakar untuk diagnosa medis menggunakan forward chaining
dan certainty factor. Sistem ini dapat menangani aturan sekuensial dan paralel.

Features:
- Forward chaining inference
- Certainty factor calculations
- GUI untuk input gejala dan output hasil
- Support untuk aturan sekuensial dan paralel
- Jejak inferensi untuk debugging

Author: Tim SISPAK 2
Version: 1.0
"""

import tkinter as tk
from tkinter import messagebox
import sys
import os

# Menambahkan path untuk import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from ui.gui import ExpertSystemGUI
    from inference_engine import InferenceEngine
except ImportError as e:
    printq(f"Error importing modules: {e}")
    print("Pastikan semua file dan folder berada di lokasi yang benar")
    sys.exit(1)

def check_requirements():
    """
    Memeriksa persyaratan sistem dan file yang diperlukan
    """
    required_files = [
        'rules.json',
        'inference_engine/forward_chaining.py',
        'ui/gui.py'
    ]
    
    missing_files = []
    for file in required_files:
        file_path = os.path.join(os.path.dirname(__file__), file)
        if not os.path.exists(file_path):
            missing_files.append(file)
    
    if missing_files:
        print("Error: File berikut tidak ditemukan:")
        for file in missing_files:
            print(f"  - {file}")
        return False
    
    # Test loading rules
    try:
        rules_path = os.path.join(os.path.dirname(__file__), 'rules.json')
        engine = InferenceEngine(rules_path)
        if not engine.rules:
            print("Error: File rules.json kosong atau tidak valid")
            return False
    except Exception as e:
        print(f"Error loading rules: {e}")
        return False
    
    return True

def show_welcome_message():
    """
    Menampilkan pesan selamat datang dan informasi sistem
    """
    print("="*60)
    print("SISTEM PAKAR DIAGNOSA MEDIS")
    print("="*60)
    print("Version: 1.0")
    print("Tim: SISPAK 2")
    print()
    print("Features:")
    print("- Forward Chaining Inference Engine")
    print("- Certainty Factor Calculations")
    print("- Sequential & Parallel Rules Support")
    print("- Graphical User Interface")
    print("- Inference Trace for Debugging")
    print()
    print("Memulai aplikasi...")
    print("="*60)

def main():
    """
    Fungsi utama aplikasi
    """
    # Tampilkan welcome message
    show_welcome_message()
    
    # Periksa persyaratan
    if not check_requirements():
        print("\\nTidak dapat memulai aplikasi karena ada file yang hilang.")
        input("Tekan Enter untuk keluar...")
        return
    
    try:
        # Buat dan jalankan GUI
        root = tk.Tk()
        
        # Set icon window (jika ada)
        try:
            # root.iconbitmap('icon.ico')  # Uncomment jika ada icon
            pass
        except Exception:
            pass
        
        # Atur behavior saat window ditutup
        def on_closing():
            if messagebox.askokcancel("Quit", "Apakah Anda yakin ingin keluar?"):
                root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Buat aplikasi
        app = ExpertSystemGUI(root)  # noqa: F841
        
        print("GUI berhasil dimuat!")
        print("Silakan gunakan interface untuk melakukan diagnosa.")
        
        # Jalankan GUI loop
        root.mainloop()
        
    except KeyboardInterrupt:
        print("\\nAplikasi dihentikan oleh user.")
    except Exception as e:
        print(f"\\nError menjalankan aplikasi: {e}")
        messagebox.showerror("Error", f"Terjadi kesalahan:\\n{str(e)}")
    
    print("\\nTerima kasih telah menggunakan Sistem Pakar Diagnosa Medis!")

if __name__ == "__main__":
    main()