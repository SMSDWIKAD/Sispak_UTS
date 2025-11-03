import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
from inferance_engine.forward_chaining import forward_chaining
import sys
import os

class SistemPakarUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistem Pakar Diagnosa Batuk")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f8ff')
        
        # Initialize system
        self.sistem = SistemPakarBatuk()
        
        # Data untuk combobox
        self.gejala_list = []
        self.load_gejala_data()
        
        # Variabel
        self.selected_gejala = []
        self.setup_ui()
    
    def load_gejala_data(self):
        """Memuat data gejala dari rules.json"""
        try:
            with open('rules.json', 'r', encoding='utf-8') as file:
                data = json.load(file)
                self.gejala_list = [
                    f"{gejala['kode']}: {gejala['nama']}" 
                    for gejala in data['data_diagnosa_batuk']['gejala']
                ]
        except Exception as e:
            messagebox.showerror("Error", f"Gagal memuat data: {str(e)}")
    
    def setup_ui(self):
        """Setup user interface"""
        # Header
        header_frame = tk.Frame(self.root, bg='#2c3e50', height=80)
        header_frame.pack(fill='x', padx=10, pady=10)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame, 
            text="SISTEM PAKAR DIAGNOSA JENIS BATUK", 
            font=('Arial', 16, 'bold'),
            fg='white',
            bg='#2c3e50'
        )
        title_label.pack(expand=True)
        
        subtitle_label = tk.Label(
            header_frame,
            text="Forward Chaining + Certainty Factor",
            font=('Arial', 10),
            fg='#ecf0f1',
            bg='#2c3e50'
        )
        subtitle_label.pack(expand=True)
        
        # Main Content Frame
        main_frame = tk.Frame(self.root, bg='#f0f8ff')
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Left Frame - Input Gejala
        left_frame = tk.LabelFrame(main_frame, text="🩺 INPUT GEJALA", 
                                 font=('Arial', 11, 'bold'),
                                 bg='#f0f8ff', fg='#2c3e50',
                                 padx=10, pady=10)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Right Frame - Hasil Diagnosa
        right_frame = tk.LabelFrame(main_frame, text="📋 HASIL DIAGNOSA", 
                                  font=('Arial', 11, 'bold'),
                                  bg='#f0f8ff', fg='#2c3e50',
                                  padx=10, pady=10)
        right_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        self.setup_input_frame(left_frame)
        self.setup_output_frame(right_frame)
    
    def setup_input_frame(self, parent):
        """Setup frame untuk input gejala"""
        # Instruction
        instruction_text = (
            "Pilih gejala yang dialami dengan mencentang checkbox di bawah.\n"
            "Sistem akan menganalisis dan memberikan diagnosa berdasarkan gejala yang dipilih."
        )
        instruction_label = tk.Label(
            parent, 
            text=instruction_text,
            font=('Arial', 9),
            bg='#f0f8ff',
            fg='#34495e',
            justify='left',
            wraplength=400
        )
        instruction_label.pack(pady=(0, 15))
        
        # Search Frame
        search_frame = tk.Frame(parent, bg='#f0f8ff')
        search_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(search_frame, text="Cari Gejala:", 
                font=('Arial', 9, 'bold'), bg='#f0f8ff').pack(side='left')
        
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, 
                               font=('Arial', 9), width=30)
        search_entry.pack(side='left', padx=(5, 0))
        search_entry.bind('<KeyRelease>', self.filter_gejala)
        
        # Gejala List Frame dengan Scrollbar
        list_frame = tk.Frame(parent, bg='#f0f8ff')
        list_frame.pack(fill='both', expand=True, pady=5)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')
        
        # Canvas untuk scrolling
        self.canvas = tk.Canvas(list_frame, yscrollcommand=scrollbar.set, 
                               bg='white', highlightthickness=0)
        self.canvas.pack(side='left', fill='both', expand=True)
        
        scrollbar.config(command=self.canvas.yview)
        
        # Frame untuk checkbox di dalam canvas
        self.checkbox_frame = tk.Frame(self.canvas, bg='white')
        self.canvas_window = self.canvas.create_window((0, 0), window=self.checkbox_frame, anchor='nw')
        
        # Bind events untuk scrolling
        self.checkbox_frame.bind('<Configure>', self.on_frame_configure)
        self.canvas.bind('<Configure>', self.on_canvas_configure)
        
        # Variabel untuk checkbox
        self.checkbox_vars = {}
        self.create_checkboxes()
        
        # Selected Gejala Display
        selected_frame = tk.Frame(parent, bg='#f0f8ff')
        selected_frame.pack(fill='x', pady=10)
        
        tk.Label(selected_frame, text="Gejala Terpilih:", 
                font=('Arial', 9, 'bold'), bg='#f0f8ff').pack(anchor='w')
        
        self.selected_text = scrolledtext.ScrolledText(
            selected_frame, 
            height=4,
            font=('Arial', 8),
            wrap=tk.WORD
        )
        self.selected_text.pack(fill='x', pady=(5, 0))
        self.selected_text.config(state='disabled')
        
        # Button Frame
        button_frame = tk.Frame(parent, bg='#f0f8ff')
        button_frame.pack(fill='x', pady=10)
        
        # Test Buttons
        test_button_frame = tk.Frame(button_frame, bg='#f0f8ff')
        test_button_frame.pack(fill='x', pady=5)
        
        tk.Label(test_button_frame, text="Test Scenario:", 
                font=('Arial', 9, 'bold'), bg='#f0f8ff').pack(side='left')
        
        test_buttons = [
            ("Pasien 1 (P1)", ["G1", "G4", "G6", "G8", "G9", "G10", "G11"]),
            ("Pasien 2 (GAGAL)", ["G4", "G2"]),
            ("Pasien 4 (P2)", ["G1", "G2", "G3", "G5", "G7", "G11"]),
            ("Pasien 6 (P3)", ["G1", "G2", "G5", "G8", "G9"])
        ]
        
        for text, gejala in test_buttons:
            btn = tk.Button(
                test_button_frame,
                text=text,
                font=('Arial', 8),
                command=lambda g=gejala: self.load_test_scenario(g),
                bg='#3498db',
                fg='white'
            )
            btn.pack(side='left', padx=2)
        
        # Action Buttons
        action_frame = tk.Frame(button_frame, bg='#f0f8ff')
        action_frame.pack(fill='x', pady=5)
        
        diagnose_btn = tk.Button(
            action_frame,
            text="🔍 LAKUKAN DIAGNOSA",
            font=('Arial', 10, 'bold'),
            command=self.run_diagnosa,
            bg='#27ae60',
            fg='white',
            padx=20,
            pady=8
        )
        diagnose_btn.pack(side='left', padx=(0, 10))
        
        clear_btn = tk.Button(
            action_frame,
            text="🔄 RESET",
            font=('Arial', 10),
            command=self.clear_all,
            bg='#e74c3c',
            fg='white',
            padx=20,
            pady=8
        )
        clear_btn.pack(side='left')
    
    def setup_output_frame(self, parent):
        """Setup frame untuk output hasil diagnosa"""
        # Process Display
        process_frame = tk.Frame(parent, bg='#f0f8ff')
        process_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(process_frame, text="Proses Inferensi:", 
                font=('Arial', 9, 'bold'), bg='#f0f8ff').pack(anchor='w')
        
        self.process_text = scrolledtext.ScrolledText(
            process_frame,
            height=8,
            font=('Consolas', 8),
            wrap=tk.WORD,
            bg='#2c3e50',
            fg='#ecf0f1'
        )
        self.process_text.pack(fill='x', pady=(5, 0))
        self.process_text.config(state='disabled')
        
        # Results Display
        results_frame = tk.Frame(parent, bg='#f0f8ff')
        results_frame.pack(fill='both', expand=True)
        
        tk.Label(results_frame, text="Hasil Diagnosa:", 
                font=('Arial', 9, 'bold'), bg='#f0f8ff').pack(anchor='w')
        
        self.results_text = scrolledtext.ScrolledText(
            results_frame,
            font=('Arial', 9),
            wrap=tk.WORD,
            bg='white'
        )
        self.results_text.pack(fill='both', expand=True, pady=(5, 0))
        self.results_text.config(state='disabled')
    
    def create_checkboxes(self):
        """Membuat checkbox untuk semua gejala"""
        for widget in self.checkbox_frame.winfo_children():
            widget.destroy()
        
        self.checkbox_vars = {}
        filtered_gejala = self.get_filtered_gejala()
        
        for i, gejala_text in enumerate(filtered_gejala):
            var = tk.BooleanVar()
            self.checkbox_vars[gejala_text] = var
            
            cb = tk.Checkbutton(
                self.checkbox_frame,
                text=gejala_text,
                variable=var,
                command=self.update_selected_display,
                font=('Arial', 8),
                bg='white',
                anchor='w'
            )
            cb.pack(fill='x', padx=5, pady=1)
    
    def get_filtered_gejala(self):
        """Mendapatkan gejala yang difilter berdasarkan pencarian"""
        search_term = self.search_var.get().lower()
        if not search_term:
            return self.gejala_list
        
        return [g for g in self.gejala_list if search_term in g.lower()]
    
    def filter_gejala(self, event=None):
        """Filter gejala berdasarkan input pencarian"""
        self.create_checkboxes()
    
    def on_frame_configure(self, event=None):
        """Update scrollregion ketika frame berubah"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def on_canvas_configure(self, event=None):
        """Update canvas window ketika canvas berubah"""
        self.canvas.itemconfig(self.canvas_window, width=event.width)
    
    def update_selected_display(self):
        """Update display gejala yang terpilih"""
        self.selected_gejala = []
        for gejala_text, var in self.checkbox_vars.items():
            if var.get():
                kode_gejala = gejala_text.split(':')[0].strip()
                self.selected_gejala.append(kode_gejala)
        
        self.selected_text.config(state='normal')
        self.selected_text.delete(1.0, tk.END)
        
        if self.selected_gejala:
            selected_display = []
            for gejala in self.selected_gejala:
                for g in self.sistem.data['data_diagnosa_batuk']['gejala']:
                    if g['kode'] == gejala:
                        selected_display.append(f"• {gejala}: {g['nama']}")
                        break
            
            self.selected_text.insert(tk.END, '\n'.join(selected_display))
        else:
            self.selected_text.insert(tk.END, "Belum ada gejala yang dipilih")
        
        self.selected_text.config(state='disabled')
    
    def load_test_scenario(self, gejala_list):
        """Memuat scenario test"""
        self.clear_all()
        
        # Centang checkbox yang sesuai
        for gejala_kode in gejala_list:
            for gejala_text, var in self.checkbox_vars.items():
                if gejala_text.startswith(gejala_kode + ':'):
                    var.set(True)
                    break
        
        self.update_selected_display()
        messagebox.showinfo("Test Scenario", f"Scenario loaded: {', '.join(gejala_list)}")
    
    def clear_all(self):
        """Reset semua input dan output"""
        for var in self.checkbox_vars.values():
            var.set(False)
        
        self.search_var.set("")
        self.update_selected_display()
        self.clear_output()
        self.create_checkboxes()
    
    def clear_output(self):
        """Clear output display"""
        self.process_text.config(state='normal')
        self.process_text.delete(1.0, tk.END)
        self.process_text.config(state='disabled')
        
        self.results_text.config(state='normal')
        self.results_text.delete(1.0, tk.END)
        self.results_text.config(state='disabled')
    
    def run_diagnosa(self):
        """Menjalankan proses diagnosa"""
        if not self.selected_gejala:
            messagebox.showwarning("Peringatan", "Pilih minimal satu gejala!")
            return
        
        self.clear_output()
        
        try:
            # Setup sistem dengan gejala terpilih
            self.sistem.facts = set(self.selected_gejala)
            self.sistem.cf_values = {}
            
            # Redirect output untuk capture proses
            import io
            from contextlib import redirect_stdout
            
            f = io.StringIO()
            
            # Run forward chaining dan capture output
            with redirect_stdout(f):
                self.sistem.forward_chaining()
            
            process_output = f.getvalue()
            
            # Tampilkan proses
            self.process_text.config(state='normal')
            self.process_text.insert(tk.END, "=== PROSES FORWARD CHAINING ===\n")
            self.process_text.insert(tk.END, process_output)
            self.process_text.config(state='disabled')
            
            # Tampilkan hasil
            self.show_results()
            
        except Exception as e:
            messagebox.showerror("Error", f"Terjadi kesalahan: {str(e)}")
    
    def show_results(self):
        """Menampilkan hasil diagnosa"""
        self.results_text.config(state='normal')
        self.results_text.delete(1.0, tk.END)
        
        # Header
        self.results_text.insert(tk.END, "🩺 HASIL DIAGNOSA BATUK\n")
        self.results_text.insert(tk.END, "="*50 + "\n\n")
        
        if not self.sistem.cf_values:
            self.results_text.insert(tk.END, "❌ Tidak dapat menentukan diagnosa.\n")
            self.results_text.insert(tk.END, "💡 Gejala yang dimasukkan tidak cukup untuk diagnosa tertentu.\n")
            self.results_text.config(state='disabled')
            return
        
        # Kategorisasi hasil
        penyakit_utama = {}
        komplikasi = {}
        
        for penyakit, cf in self.sistem.cf_values.items():
            if penyakit.startswith('P') and penyakit in ['P1', 'P2', 'P3']:
                penyakit_utama[penyakit] = cf
            elif penyakit.startswith('KOMPLIKASI'):
                komplikasi[penyakit] = cf
        
        # Tampilkan penyakit utama
        if penyakit_utama:
            self.results_text.insert(tk.END, "📋 DIAGNOSA UTAMA:\n\n")
            
            for penyakit, cf in sorted(penyakit_utama.items(), key=lambda x: x[1], reverse=True):
                nama_penyakit = self.sistem.get_penyakit_by_kode(penyakit)
                persentase = cf * 100
                
                # Warna berdasarkan CF
                if cf >= 0.7:
                    color = "#27ae60"  # Hijau untuk CF tinggi
                elif cf >= 0.4:
                    color = "#f39c12"  # Orange untuk CF medium
                else:
                    color = "#e74c3c"  # Merah untuk CF rendah
                
                self.results_text.insert(tk.END, f"🔸 ", "bold")
                self.results_text.insert(tk.END, f"{nama_penyakit}\n")
                self.results_text.insert(tk.END, f"   Certainty Factor: ", "bold")
                self.results_text.insert(tk.END, f"{cf:.3f} ", f"color_{color}")
                self.results_text.insert(tk.END, f"({persentase:.1f}%)\n")
                
                # Rekomendasi
                if penyakit == 'P1':
                    self.results_text.insert(tk.END, f"   💊 Rekomendasi: Obat ekspektoran untuk mengeluarkan dahak\n")
                elif penyakit == 'P2':
                    self.results_text.insert(tk.END, f"   💊 Rekomendasi: Obat antitusif untuk menekan batuk\n")
                elif penyakit == 'P3':
                    self.results_text.insert(tk.END, f"   💊 Rekomendasi: Obat antihistamin dan hindari alergen\n")
                
                self.results_text.insert(tk.END, "\n")
        
        # Tampilkan komplikasi
        if komplikasi:
            self.results_text.insert(tk.END, "⚠️  KOMPLIKASI YANG MUNGKIN:\n\n")
            for komp, cf in sorted(komplikasi.items(), key=lambda x: x[1], reverse=True):
                persentase = cf * 100
                nama_komp = komp.replace('_', ' ').title()
                self.results_text.insert(tk.END, f"• {nama_komp}: {cf:.3f} ({persentase:.1f}%)\n")
            self.results_text.insert(tk.END, "\n")
        
        # Status khusus
        if 'GAGAL' in self.sistem.cf_values:
            self.results_text.insert(tk.END, "❌ STATUS: Tidak dapat didiagnosa\n")
            self.results_text.insert(tk.END, "💡 Disarankan untuk konsultasi dengan dokter\n")
        
        if not penyakit_utama and 'GAGAL' not in self.sistem.cf_values:
            self.results_text.insert(tk.END, "❓ STATUS: Diagnosa tidak pasti\n")
            self.results_text.insert(tk.END, "💡 Gejala tidak spesifik, perlu pemeriksaan lebih lanjut\n")
        
        # Configure tags untuk styling
        self.results_text.tag_configure("bold", font=('Arial', 9, 'bold'))
        self.results_text.tag_configure("color_#27ae60", foreground="#27ae60")
        self.results_text.tag_configure("color_#f39c12", foreground="#f39c12")
        self.results_text.tag_configure("color_#e74c3c", foreground="#e74c3c")
        
        self.results_text.config(state='disabled')

def main():
    """Main function"""
    root = tk.Tk()
    app = SistemPakarUI(root)
    root.mainloop()

if __name__ == "__main__":
    # Check if rules.json exists
    if not os.path.exists('rules.json'):
        messagebox.showerror("Error", "File rules.json tidak ditemukan!")
        sys.exit(1)
    
    main()