#!/usr/bin/env python3
"""
Command Line Interface untuk Sistem Pakar
==========================================

Interface command line untuk testing dan demonstrasi sistem pakar
tanpa GUI.
"""

import os
import sys
import json

# Menambahkan path untuk import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from inference_engine import InferenceEngine

class ExpertSystemCLI:
    """
    Command Line Interface untuk Expert System
    """
    
    def __init__(self):
        rules_path = os.path.join(os.path.dirname(__file__), 'rules.json')
        self.inference_engine = InferenceEngine(rules_path)
        
        # Load available symptoms from rules
        self.available_symptoms = set()
        for rule in self.inference_engine.rules:
            for symptom in rule['if']:
                self.available_symptoms.add(symptom)
        self.available_symptoms = sorted(list(self.available_symptoms))
    
    def display_welcome(self):
        """Menampilkan welcome message"""
        print("\\n" + "="*60)
        print("SISTEM PAKAR DIAGNOSA MEDIS - CLI MODE")
        print("="*60)
        print("Tim: SISPAK 2")
        print("Version: 1.0")
        print("\\nSistem ini menggunakan forward chaining dengan certainty factor")
        print("untuk melakukan diagnosa berdasarkan gejala yang diinput.")
        print("="*60)
    
    def display_symptoms(self):
        """Menampilkan daftar gejala yang tersedia"""
        print("\\nGejala yang tersedia:")
        print("-" * 30)
        for i, symptom in enumerate(self.available_symptoms, 1):
            display_name = symptom.replace('_', ' ').title()
            print(f"{i:2d}. {display_name}")
        print()
    
    def get_user_input(self):
        """Mendapatkan input gejala dari user"""
        selected_symptoms = {}
        
        print("Pilih gejala yang dialami pasien:")
        print("(Masukkan nomor gejala diikuti certainty factor, contoh: 1 0.8)")
        print("(Ketik 'selesai' untuk mengakhiri input)")
        print("(Ketik 'list' untuk melihat daftar gejala)")
        print()
        
        while True:
            try:
                user_input = input("Input gejala: ").strip().lower()
                
                if user_input == 'selesai':
                    break
                elif user_input == 'list':
                    self.display_symptoms()
                    continue
                elif user_input == 'help':
                    print("\\nFormat input: [nomor] [certainty_factor]")
                    print("Contoh: 1 0.8 (memilih gejala nomor 1 dengan CF 0.8)")
                    print("CF harus antara 0.1 - 1.0")
                    continue
                
                # Parse input
                parts = user_input.split()
                if len(parts) != 2:
                    print("Format salah! Gunakan: [nomor] [cf]. Ketik 'help' untuk bantuan.")
                    continue
                
                symptom_num = int(parts[0])
                cf_value = float(parts[1])
                
                # Validasi nomor gejala
                if not (1 <= symptom_num <= len(self.available_symptoms)):
                    print(f"Nomor gejala harus antara 1-{len(self.available_symptoms)}")
                    continue
                
                # Validasi CF
                if not (0.1 <= cf_value <= 1.0):
                    print("Certainty factor harus antara 0.1 - 1.0")
                    continue
                
                # Tambahkan gejala
                symptom = self.available_symptoms[symptom_num - 1]
                selected_symptoms[symptom] = cf_value
                
                display_name = symptom.replace('_', ' ').title()
                print(f"✓ Ditambahkan: {display_name} (CF: {cf_value})")
                
            except ValueError:
                print("Input tidak valid! Gunakan format: [nomor] [cf]")
            except KeyboardInterrupt:
                print("\\nInput dibatalkan.")
                return None
        
        if not selected_symptoms:
            print("Tidak ada gejala yang dipilih!")
            return None
        
        return selected_symptoms
    
    def run_diagnosis(self, symptoms):
        """Menjalankan diagnosa"""
        print("\\n" + "="*50)
        print("MENJALANKAN DIAGNOSA...")
        print("="*50)
        
        # Reset inference engine
        self.inference_engine.reset()
        
        # Tambahkan gejala sebagai fakta awal
        print("\\nFakta awal:")
        for symptom, cf in symptoms.items():
            display_name = symptom.replace('_', ' ').title()
            print(f"  - {display_name}: CF = {cf}")
        
        self.inference_engine.add_initial_facts(symptoms)
        
        # Jalankan forward chaining
        print("\\nMemulai forward chaining...")
        results = self.inference_engine.forward_chaining()
        
        return results
    
    def display_results(self, results):
        """Menampilkan hasil diagnosa"""
        print("\\n" + "="*50)
        print("HASIL DIAGNOSA")
        print("="*50)
        
        if not results:
            print("Tidak ada kesimpulan yang dapat ditarik.")
            return
        
        # Filter dan urutkan hasil
        significant_results = {k: v for k, v in results.items() if v >= 0.1}
        sorted_results = sorted(significant_results.items(), key=lambda x: x[1], reverse=True)
        
        print("\\nKesimpulan yang dapat ditarik:")
        print("-" * 40)
        
        for fact, cf in sorted_results:
            confidence_level = self.get_confidence_level(cf)
            display_name = fact.replace('_', ' ').title()
            print(f"• {display_name}")
            print(f"  CF: {cf:.3f} ({confidence_level})")
            print()
        
        # Kesimpulan utama
        most_likely, highest_cf = self.inference_engine.get_most_likely_conclusion()
        if most_likely:
            print("KESIMPULAN UTAMA:")
            print("-" * 20)
            display_name = most_likely.replace('_', ' ').title()
            print(f"• {display_name}")
            print(f"  Tingkat Keyakinan: {highest_cf:.3f}")
            print(f"  Level: {self.get_confidence_level(highest_cf)}")
        
        # Rules yang digunakan
        fired_rules = self.inference_engine.fired_rules
        if fired_rules:
            print(f"\\nRules yang digunakan: {', '.join(fired_rules)}")
        
        print(f"Total fakta diturunkan: {len(results)}")
    
    def get_confidence_level(self, cf):
        """Mendapatkan level keyakinan berdasarkan CF"""
        if cf >= 0.8:
            return "Sangat Tinggi"
        elif cf >= 0.6:
            return "Tinggi"
        elif cf >= 0.4:
            return "Sedang"
        else:
            return "Rendah"
    
    def show_inference_trace(self):
        """Menampilkan jejak inferensi"""
        trace = self.inference_engine.get_inference_trace()
        
        if not trace:
            print("Tidak ada jejak inferensi.")
            return
        
        print("\\n" + "="*50)
        print("JEJAK INFERENSI")
        print("="*50)
        
        for step in trace:
            print(step)
    
    def run(self):
        """Menjalankan CLI interface"""
        self.display_welcome()
        
        while True:
            try:
                print("\\n" + "="*30)
                print("MENU UTAMA")
                print("="*30)
                print("1. Mulai Diagnosa")
                print("2. Lihat Daftar Gejala")
                print("3. Lihat Rules")
                print("4. Keluar")
                
                choice = input("\\nPilih menu (1-4): ").strip()
                
                if choice == '1':
                    self.display_symptoms()
                    symptoms = self.get_user_input()
                    
                    if symptoms:
                        results = self.run_diagnosis(symptoms)
                        self.display_results(results)
                        
                        # Tanya apakah ingin melihat trace
                        show_trace = input("\\nTampilkan jejak inferensi? (y/n): ").strip().lower()
                        if show_trace == 'y':
                            self.show_inference_trace()
                
                elif choice == '2':
                    self.display_symptoms()
                
                elif choice == '3':
                    self.display_rules()
                
                elif choice == '4':
                    print("\\nTerima kasih telah menggunakan Sistem Pakar!")
                    break
                
                else:
                    print("Pilihan tidak valid!")
                
            except KeyboardInterrupt:
                print("\\n\\nProgram dihentikan oleh user.")
                break
            except Exception as e:
                print(f"\\nError: {e}")
    
    def display_rules(self):
        """Menampilkan daftar rules"""
        print("\\n" + "="*50)
        print("DAFTAR RULES")
        print("="*50)
        
        for rule in self.inference_engine.rules:
            print(f"\\n{rule['id']}: {rule.get('description', 'Tidak ada deskripsi')}")
            
            premises = [p.replace('_', ' ').title() for p in rule['if']]
            conclusion = rule['then'].replace('_', ' ').title()
            
            print(f"  IF: {' AND '.join(premises)}")
            print(f"  THEN: {conclusion}")
            print(f"  CF: {rule['cf']}")

def main():
    """Fungsi utama"""
    try:
        cli = ExpertSystemCLI()
        cli.run()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()