#!/usr/bin/env python3
"""
Sistem Pakar Diagnosa Medis - Launcher Utama
============================================

Launcher untuk menjalankan sistem pakar dalam berbagai mode:
- GUI Mode (Desktop Application)
- Web Mode (Web Browser Application)
- CLI Mode (Command Line Interface)

Author: Tim SISPAK 2
Version: 2.0 (Multi-Interface Edition)
"""

import os
import sys
import subprocess
import tkinter as tk
from tkinter import messagebox, ttk
import webbrowser
import threading
import time

class SystemLauncher:
    """Launcher untuk memilih mode aplikasi sistem pakar"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sistem Pakar Diagnosa Medis - Launcher")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # Center window
        self.center_window()
        
        # Variables
        self.flask_process = None
        
        self.create_widgets()
        
    def center_window(self):
        """Center window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Create launcher interface"""
        
        # Header
        header_frame = tk.Frame(self.root, bg='#2c3e50', height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, 
                             text="SISTEM PAKAR DIAGNOSA MEDIS",
                             font=('Arial', 18, 'bold'),
                             fg='white', bg='#2c3e50')
        title_label.pack(expand=True)
        
        subtitle_label = tk.Label(header_frame,
                                text="Forward Chaining dengan Certainty Factor",
                                font=('Arial', 10),
                                fg='#ecf0f1', bg='#2c3e50')
        subtitle_label.pack()
        
        # Main content
        main_frame = tk.Frame(self.root, bg='#ecf0f1', padx=40, pady=30)
        main_frame.pack(fill='both', expand=True)
        
        # Description
        desc_label = tk.Label(main_frame,
                            text="Pilih mode aplikasi yang ingin digunakan:",
                            font=('Arial', 12),
                            bg='#ecf0f1', fg='#2c3e50')
        desc_label.pack(pady=(0, 20))
        
        # Mode buttons
        self.create_mode_buttons(main_frame)
        
        # Info section
        self.create_info_section(main_frame)
        
        # Footer
        footer_frame = tk.Frame(self.root, bg='#34495e', height=40)
        footer_frame.pack(fill='x', side='bottom')
        footer_frame.pack_propagate(False)
        
        footer_label = tk.Label(footer_frame,
                              text="Tim SISPAK 2 - Version 2.0 © 2025",
                              font=('Arial', 9),
                              fg='white', bg='#34495e')
        footer_label.pack(expand=True)
        
    def create_mode_buttons(self, parent):
        """Create mode selection buttons"""
        
        buttons_frame = tk.Frame(parent, bg='#ecf0f1')
        buttons_frame.pack(pady=20)
        
        # Web Mode Button
        web_frame = tk.Frame(buttons_frame, bg='white', relief='raised', bd=2, padx=20, pady=15)
        web_frame.pack(fill='x', pady=10)
        
        web_title = tk.Label(web_frame, 
                           text="🌐 Web Mode (Recommended)",
                           font=('Arial', 14, 'bold'),
                           bg='white', fg='#27ae60')
        web_title.pack()
        
        web_desc = tk.Label(web_frame,
                          text="Interface web modern dengan fitur lengkap\nBuka di browser, responsive design",
                          font=('Arial', 10),
                          bg='white', fg='#7f8c8d', justify='center')
        web_desc.pack(pady=5)
        
        web_btn = tk.Button(web_frame,
                          text="Buka Web Interface",
                          command=self.launch_web_mode,
                          bg='#27ae60', fg='white',
                          font=('Arial', 11, 'bold'),
                          relief='flat', padx=30, pady=8,
                          cursor='hand2')
        web_btn.pack(pady=5)
        
        # Desktop Mode Button
        desktop_frame = tk.Frame(buttons_frame, bg='white', relief='raised', bd=2, padx=20, pady=15)
        desktop_frame.pack(fill='x', pady=10)
        
        desktop_title = tk.Label(desktop_frame,
                               text="🖥️ Desktop Mode",
                               font=('Arial', 14, 'bold'),
                               bg='white', fg='#3498db')
        desktop_title.pack()
        
        desktop_desc = tk.Label(desktop_frame,
                              text="Aplikasi desktop dengan tkinter\nInterface klasik, tidak perlu browser",
                              font=('Arial', 10),
                              bg='white', fg='#7f8c8d', justify='center')
        desktop_desc.pack(pady=5)
        
        desktop_btn = tk.Button(desktop_frame,
                              text="Buka Desktop App",
                              command=self.launch_desktop_mode,
                              bg='#3498db', fg='white',
                              font=('Arial', 11, 'bold'),
                              relief='flat', padx=30, pady=8,
                              cursor='hand2')
        desktop_btn.pack(pady=5)
        
        # CLI Mode Button
        cli_frame = tk.Frame(buttons_frame, bg='white', relief='raised', bd=2, padx=20, pady=15)
        cli_frame.pack(fill='x', pady=10)
        
        cli_title = tk.Label(cli_frame,
                           text="⌨️ CLI Mode",
                           font=('Arial', 14, 'bold'),
                           bg='white', fg='#e67e22')
        cli_title.pack()
        
        cli_desc = tk.Label(cli_frame,
                          text="Command line interface untuk testing\nMode teks, cocok untuk debugging",
                          font=('Arial', 10),
                          bg='white', fg='#7f8c8d', justify='center')
        cli_desc.pack(pady=5)
        
        cli_btn = tk.Button(cli_frame,
                          text="Buka CLI Mode",
                          command=self.launch_cli_mode,
                          bg='#e67e22', fg='white',
                          font=('Arial', 11, 'bold'),
                          relief='flat', padx=30, pady=8,
                          cursor='hand2')
        cli_btn.pack(pady=5)
    
    def create_info_section(self, parent):
        """Create information section"""
        
        info_frame = tk.LabelFrame(parent, text="Informasi Sistem", 
                                 font=('Arial', 10, 'bold'),
                                 bg='#ecf0f1', fg='#2c3e50',
                                 padx=15, pady=10)
        info_frame.pack(fill='x', pady=20)
        
        info_text = """
📊 15 Aturan Medis    🧠 Forward Chaining Algorithm
🔍 21 Gejala Medis    📈 Certainty Factor Support
🏥 Domain: Infeksi, Pneumonia, Gastroenteritis
🔄 Aturan Sekuensial & Paralel
        """
        
        info_label = tk.Label(info_frame, text=info_text.strip(),
                            font=('Arial', 9),
                            bg='#ecf0f1', fg='#34495e',
                            justify='left')
        info_label.pack()
        
    def launch_web_mode(self):
        """Launch web interface"""
        try:
            # Start Flask server in background
            self.start_flask_server()
            
            # Show loading message
            loading_window = self.show_loading_window("Starting web server...")
            
            # Wait a moment for server to start
            self.root.after(3000, lambda: self.open_browser_and_close_loading(loading_window))
            
        except Exception as e:
            messagebox.showerror("Error", f"Gagal memulai web server:\\n{str(e)}")
    
    def start_flask_server(self):
        """Start Flask server in background"""
        def run_flask():
            try:
                # Path to Flask app
                app_path = os.path.join(os.path.dirname(__file__), 'web_ui', 'app.py')
                python_path = self.get_python_path()
                
                # Start Flask process
                self.flask_process = subprocess.Popen([python_path, app_path],
                                                    stdout=subprocess.PIPE,
                                                    stderr=subprocess.PIPE,
                                                    cwd=os.path.dirname(app_path))
                
            except Exception as e:
                print(f"Error starting Flask: {e}")
        
        # Run in separate thread
        flask_thread = threading.Thread(target=run_flask, daemon=True)
        flask_thread.start()
    
    def open_browser_and_close_loading(self, loading_window):
        """Open browser and close loading window"""
        loading_window.destroy()
        
        # Open browser
        webbrowser.open('http://localhost:5000')
        
        # Show success message
        messagebox.showinfo("Web Mode", 
                          "Web interface telah dibuka di browser!\\n\\n" +
                          "URL: http://localhost:5000\\n\\n" +
                          "Jika browser tidak terbuka otomatis, buka URL tersebut secara manual.")
        
        # Option to close launcher or keep running
        result = messagebox.askyesno("Web Server", 
                                   "Web server sedang berjalan.\\n\\n" +
                                   "Tutup launcher ini?\\n\\n" +
                                   "• Ya: Tutup launcher (server tetap jalan)\\n" +
                                   "• Tidak: Biarkan launcher terbuka")
        
        if result:
            self.root.quit()
    
    def launch_desktop_mode(self):
        """Launch desktop GUI"""
        try:
            from ui.gui import ExpertSystemGUI
            
            # Close launcher
            self.root.withdraw()
            
            # Start desktop app
            desktop_root = tk.Toplevel()
            app = ExpertSystemGUI(desktop_root)
            
            # When desktop app closes, show launcher again
            def on_desktop_close():
                desktop_root.destroy()
                self.root.deiconify()
            
            desktop_root.protocol("WM_DELETE_WINDOW", on_desktop_close)
            
        except Exception as e:
            messagebox.showerror("Error", f"Gagal memulai desktop mode:\\n{str(e)}")
            self.root.deiconify()
    
    def launch_cli_mode(self):
        """Launch CLI mode"""
        try:
            cli_path = os.path.join(os.path.dirname(__file__), 'cli.py')
            python_path = self.get_python_path()
            
            # Start CLI in new terminal window
            if os.name == 'nt':  # Windows
                subprocess.Popen(['cmd', '/c', 'start', 'cmd', '/k', python_path, cli_path])
            else:  # Linux/Mac
                subprocess.Popen(['gnome-terminal', '--', python_path, cli_path])
            
            messagebox.showinfo("CLI Mode", 
                              "Command Line Interface telah dibuka di terminal baru!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Gagal memulai CLI mode:\\n{str(e)}")
    
    def show_loading_window(self, message):
        """Show loading window"""
        loading = tk.Toplevel(self.root)
        loading.title("Loading...")
        loading.geometry("300x150")
        loading.resizable(False, False)
        loading.transient(self.root)
        loading.grab_set()
        
        # Center loading window
        loading.update_idletasks()
        x = (loading.winfo_screenwidth() // 2) - (150)
        y = (loading.winfo_screenheight() // 2) - (75)
        loading.geometry(f'300x150+{x}+{y}')
        
        # Loading content
        tk.Label(loading, text=message, 
                font=('Arial', 12), pady=20).pack()
        
        # Progress bar
        progress = ttk.Progressbar(loading, mode='indeterminate', length=200)
        progress.pack(pady=10)
        progress.start()
        
        tk.Label(loading, text="Please wait...", 
                font=('Arial', 9), fg='gray').pack()
        
        return loading
    
    def get_python_path(self):
        """Get Python executable path"""
        # Try to find virtual environment Python
        venv_paths = [
            os.path.join(os.path.dirname(__file__), '..', '.venv', 'Scripts', 'python.exe'),
            os.path.join(os.path.dirname(__file__), 'venv', 'Scripts', 'python.exe'),
            sys.executable
        ]
        
        for path in venv_paths:
            if os.path.exists(path):
                return path
        
        return 'python'  # Fallback
    
    def on_closing(self):
        """Handle window closing"""
        if self.flask_process:
            try:
                self.flask_process.terminate()
            except:
                pass
        
        self.root.destroy()
    
    def run(self):
        """Run the launcher"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

def main():
    """Main function"""
    try:
        launcher = SystemLauncher()
        launcher.run()
    except Exception as e:
        print(f"Error starting launcher: {e}")
        messagebox.showerror("Error", f"Gagal memulai launcher:\\n{str(e)}")

if __name__ == "__main__":
    main()