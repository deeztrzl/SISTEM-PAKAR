import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sys
import os

# Menambahkan path untuk import module lokal
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from inference_engine import InferenceEngine

class ExpertSystemGUI:
    """
    GUI untuk Expert System dengan tkinter
    Menyediakan antarmuka untuk input gejala dan menampilkan hasil inferensi
    """
    
    def __init__(self, root):
        self.root = root
        self.root.title("Sistem Pakar Diagnosa Medis")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        
        # Inisialisasi inference engine
        rules_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'rules.json')
        self.inference_engine = InferenceEngine(rules_path)
        
        # Daftar gejala yang tersedia
        self.available_symptoms = [
            "demam_tinggi", "sakit_kepala", "batuk_kering", "sesak_napas",
            "mual", "muntah", "diare", "leukositosis", "infiltrat_paru",
            "batuk_produktif", "nyeri_dada", "dehidrasi", "tidak_responsif_antibiotik",
            "gagal_napas", "ruam_kulit", "nyeri_sendi", "limfositosis",
            "syok_hipovolemik", "sepsis", "kultur_positif", "komplikasi_sekunder"
        ]
        
        self.selected_symptoms = {}  # {symptom: cf_value}
        
        self.create_widgets()
    
    def create_widgets(self):
        """Membuat semua widget GUI"""
        
        # Title
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=60)
        title_frame.pack(fill='x', pady=(0, 10))
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, text="SISTEM PAKAR DIAGNOSA MEDIS", 
                              font=('Arial', 18, 'bold'), fg='white', bg='#2c3e50')
        title_label.pack(expand=True)
        
        # Main container
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Left panel - Input gejala
        left_frame = tk.LabelFrame(main_frame, text="Input Gejala Pasien", 
                                  font=('Arial', 12, 'bold'), bg='#f0f0f0', padx=10, pady=10)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Instructions
        instruction_label = tk.Label(left_frame, 
                                    text="Pilih gejala yang dialami pasien dan tentukan tingkat keyakinan (0.1 - 1.0):",
                                    font=('Arial', 10), bg='#f0f0f0', wraplength=400)
        instruction_label.pack(anchor='w', pady=(0, 10))
        
        # Scrollable frame untuk symptoms
        canvas = tk.Canvas(left_frame, bg='#f0f0f0', height=400)
        scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#f0f0f0')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create symptom checkboxes dan entry fields
        self.symptom_vars = {}
        self.cf_entries = {}
        
        for i, symptom in enumerate(self.available_symptoms):
            frame = tk.Frame(scrollable_frame, bg='#f0f0f0')
            frame.pack(fill='x', pady=2)
            
            # Checkbox
            var = tk.BooleanVar()
            self.symptom_vars[symptom] = var
            
            checkbox = tk.Checkbutton(frame, text=symptom.replace('_', ' ').title(), 
                                    variable=var, bg='#f0f0f0', font=('Arial', 9),
                                    command=lambda s=symptom: self.toggle_symptom(s))
            checkbox.pack(side='left', anchor='w')
            
            # CF Entry
            cf_frame = tk.Frame(frame, bg='#f0f0f0')
            cf_frame.pack(side='right')
            
            tk.Label(cf_frame, text="CF:", font=('Arial', 8), bg='#f0f0f0').pack(side='left')
            
            cf_entry = tk.Entry(cf_frame, width=6, font=('Arial', 8))
            cf_entry.insert(0, "0.8")
            cf_entry.configure(state='disabled')
            self.cf_entries[symptom] = cf_entry
            cf_entry.pack(side='left', padx=(2, 0))
        
        # Buttons frame
        button_frame = tk.Frame(left_frame, bg='#f0f0f0')
        button_frame.pack(fill='x', pady=10)
        
        # Diagnose button
        diagnose_btn = tk.Button(button_frame, text="DIAGNOSA", 
                               command=self.run_diagnosis,
                               bg='#27ae60', fg='white', font=('Arial', 12, 'bold'),
                               height=2, cursor='hand2')
        diagnose_btn.pack(side='left', padx=(0, 10), fill='x', expand=True)
        
        # Reset button
        reset_btn = tk.Button(button_frame, text="RESET", 
                            command=self.reset_form,
                            bg='#e74c3c', fg='white', font=('Arial', 12, 'bold'),
                            height=2, cursor='hand2')
        reset_btn.pack(side='left', fill='x', expand=True)
        
        # Right panel - Results
        right_frame = tk.LabelFrame(main_frame, text="Hasil Diagnosa", 
                                   font=('Arial', 12, 'bold'), bg='#f0f0f0', padx=10, pady=10)
        right_frame.pack(side='right', fill='both', expand=True)
        
        # Results text area
        self.results_text = scrolledtext.ScrolledText(right_frame, 
                                                     font=('Consolas', 10),
                                                     height=20, width=50,
                                                     bg='white', fg='black')
        self.results_text.pack(fill='both', expand=True, pady=(0, 10))
        
        # Trace button
        trace_btn = tk.Button(right_frame, text="Tampilkan Jejak Inferensi", 
                            command=self.show_inference_trace,
                            bg='#3498db', fg='white', font=('Arial', 10),
                            cursor='hand2')
        trace_btn.pack(fill='x')
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Siap untuk diagnosa")
        status_bar = tk.Label(self.root, textvariable=self.status_var, 
                            relief=tk.SUNKEN, anchor=tk.W, bg='#ecf0f1', font=('Arial', 9))
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def toggle_symptom(self, symptom):
        """Toggle state CF entry berdasarkan checkbox"""
        if self.symptom_vars[symptom].get():
            self.cf_entries[symptom].configure(state='normal')
            self.cf_entries[symptom].configure(bg='white')
        else:
            self.cf_entries[symptom].configure(state='disabled')
            self.cf_entries[symptom].configure(bg='#f0f0f0')
    
    def validate_inputs(self):
        """Validasi input gejala dan CF"""
        selected_symptoms = {}
        
        for symptom in self.available_symptoms:
            if self.symptom_vars[symptom].get():
                try:
                    cf_value = float(self.cf_entries[symptom].get())
                    if not (0.1 <= cf_value <= 1.0):
                        messagebox.showerror("Error", 
                                           f"CF untuk {symptom} harus antara 0.1 dan 1.0")
                        return None
                    selected_symptoms[symptom] = cf_value
                except ValueError:
                    messagebox.showerror("Error", 
                                       f"CF untuk {symptom} harus berupa angka")
                    return None
        
        if not selected_symptoms:
            messagebox.showwarning("Warning", "Pilih minimal satu gejala!")
            return None
        
        return selected_symptoms
    
    def run_diagnosis(self):
        """Menjalankan proses diagnosa"""
        # Validasi input
        symptoms = self.validate_inputs()
        if symptoms is None:
            return
        
        self.status_var.set("Menjalankan diagnosa...")
        self.root.update()
        
        try:
            # Reset inference engine
            self.inference_engine.reset()
            
            # Tambahkan gejala sebagai fakta awal
            self.inference_engine.add_initial_facts(symptoms)
            
            # Jalankan forward chaining
            results = self.inference_engine.forward_chaining()
            
            # Tampilkan hasil
            self.display_results(symptoms, results)
            
            self.status_var.set(f"Diagnosa selesai - {len(results)} fakta diturunkan")
            
        except Exception as e:
            messagebox.showerror("Error", f"Terjadi kesalahan: {str(e)}")
            self.status_var.set("Error dalam diagnosa")
    
    def display_results(self, input_symptoms, results):
        """Menampilkan hasil diagnosa"""
        self.results_text.delete(1.0, tk.END)
        
        # Header
        self.results_text.insert(tk.END, "="*50 + "\\n")
        self.results_text.insert(tk.END, "HASIL DIAGNOSA SISTEM PAKAR\\n")
        self.results_text.insert(tk.END, "="*50 + "\\n\\n")
        
        # Input gejala
        self.results_text.insert(tk.END, "GEJALA INPUT:\\n")
        self.results_text.insert(tk.END, "-"*20 + "\\n")
        for symptom, cf in input_symptoms.items():
            display_name = symptom.replace('_', ' ').title()
            self.results_text.insert(tk.END, f"• {display_name}: CF = {cf:.2f}\\n")
        
        # Hasil inferensi
        self.results_text.insert(tk.END, "\\nHASIL INFERENSI:\\n")
        self.results_text.insert(tk.END, "-"*20 + "\\n")
        
        if results:
            # Urutkan berdasarkan CF
            sorted_results = sorted(results.items(), key=lambda x: x[1], reverse=True)
            
            for fact, cf in sorted_results:
                if cf >= 0.1:  # Hanya tampilkan yang signifikan
                    confidence_level = self.get_confidence_level(cf)
                    display_name = fact.replace('_', ' ').title()
                    self.results_text.insert(tk.END, f"• {display_name}\\n")
                    self.results_text.insert(tk.END, f"  CF: {cf:.3f} ({confidence_level})\\n\\n")
            
            # Kesimpulan utama
            most_likely, highest_cf = self.inference_engine.get_most_likely_conclusion()
            if most_likely:
                self.results_text.insert(tk.END, "\\nKESIMPULAN UTAMA:\\n")
                self.results_text.insert(tk.END, "-"*20 + "\\n")
                display_name = most_likely.replace('_', ' ').title()
                self.results_text.insert(tk.END, f"• {display_name}\\n")
                self.results_text.insert(tk.END, f"  Tingkat Keyakinan: {highest_cf:.3f}\\n")
                self.results_text.insert(tk.END, f"  Level: {self.get_confidence_level(highest_cf)}\\n")
        else:
            self.results_text.insert(tk.END, "Tidak ada kesimpulan yang dapat ditarik.\\n")
        
        # Rules yang digunakan
        fired_rules = self.inference_engine.fired_rules
        if fired_rules:
            self.results_text.insert(tk.END, f"\\nRULES YANG DIGUNAKAN: {', '.join(fired_rules)}\\n")
    
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
        """Menampilkan jejak inferensi dalam window terpisah"""
        trace = self.inference_engine.get_inference_trace()
        
        if not trace:
            messagebox.showinfo("Info", "Belum ada jejak inferensi. Jalankan diagnosa terlebih dahulu.")
            return
        
        # Window baru untuk trace
        trace_window = tk.Toplevel(self.root)
        trace_window.title("Jejak Inferensi")
        trace_window.geometry("700x500")
        
        # Text area untuk trace
        trace_text = scrolledtext.ScrolledText(trace_window, font=('Consolas', 10))
        trace_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Tampilkan trace
        for step in trace:
            trace_text.insert(tk.END, step + "\\n")
        
        trace_text.configure(state='disabled')
    
    def reset_form(self):
        """Reset form ke kondisi awal"""
        # Uncheck semua checkbox
        for var in self.symptom_vars.values():
            var.set(False)
        
        # Disable semua CF entries dan reset nilai
        for entry in self.cf_entries.values():
            entry.configure(state='normal')
            entry.delete(0, tk.END)
            entry.insert(0, "0.8")
            entry.configure(state='disabled', bg='#f0f0f0')
        
        # Clear results
        self.results_text.delete(1.0, tk.END)
        
        # Reset inference engine
        self.inference_engine.reset()
        
        self.status_var.set("Form telah direset")

def main():
    """Fungsi utama untuk menjalankan aplikasi"""
    root = tk.Tk()
    app = ExpertSystemGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()