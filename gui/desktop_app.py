#!/usr/bin/env python3
"""
🖥️ Interface Graphique Desktop - Audiobook Manager Pro
Interface Tkinter pour une utilisation desktop simplifiée
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import queue
import json
import os
import sys
from pathlib import Path

# Ajout du path du projet
sys.path.append(str(Path(__file__).parent.parent))

from core.processor import AudiobookProcessor
from core.config import ProcessingConfig
from web.app import conversion_status

class AudiobookManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎧 Audiobook Manager Pro v2.0")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Configuration des styles
        self.setup_styles()
        
        # Queue pour la communication entre threads
        self.queue = queue.Queue()
        
        # Variables de configuration
        self.source_dir = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.processing_mode = tk.StringVar(value="encode_aac")
        self.audio_bitrate = tk.StringVar(value="128k")
        self.sample_rate = tk.IntVar(value=48000)
        self.enable_gpu = tk.BooleanVar(value=False)
        self.enable_loudnorm = tk.BooleanVar(value=True)
        
        # Variables de progression
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value="Prêt")
        self.current_file_var = tk.StringVar(value="")
        
        # Création de l'interface
        self.create_widgets()
        
        # Démarrage du monitoring de la queue
        self.root.after(100, self.process_queue)
        
    def setup_styles(self):
        """Configuration des styles ttk"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configuration des couleurs
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Success.TLabel', foreground='green')
        style.configure('Error.TLabel', foreground='red')
        style.configure('Warning.TLabel', foreground='orange')
        
    def create_widgets(self):
        """Création de tous les widgets"""
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configuration du poids pour le redimensionnement
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Titre
        title_label = ttk.Label(main_frame, text="🎧 Audiobook Manager Pro", style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Configuration des répertoires
        self.create_directory_section(main_frame)
        
        # Configuration audio
        self.create_audio_section(main_frame)
        
        # Contrôles
        self.create_control_section(main_frame)
        
        # Progression
        self.create_progress_section(main_frame)
        
        # Logs
        self.create_log_section(main_frame)
        
    def create_directory_section(self, parent):
        """Section configuration des répertoires"""
        frame = ttk.LabelFrame(parent, text="📁 Répertoires", padding="10")
        frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        frame.columnconfigure(1, weight=1)
        
        # Répertoire source
        ttk.Label(frame, text="Source:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Entry(frame, textvariable=self.source_dir, width=50).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=2)
        ttk.Button(frame, text="Parcourir...", command=self.browse_source).grid(row=0, column=2, pady=2)
        
        # Répertoire de sortie
        ttk.Label(frame, text="Sortie:").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Entry(frame, textvariable=self.output_dir, width=50).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=2)
        ttk.Button(frame, text="Parcourir...", command=self.browse_output).grid(row=1, column=2, pady=2)
        
    def create_audio_section(self, parent):
        """Section configuration audio"""
        frame = ttk.LabelFrame(parent, text="🎵 Configuration Audio", padding="10")
        frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        frame.columnconfigure(1, weight=1)
        
        # Mode de traitement
        ttk.Label(frame, text="Mode:").grid(row=0, column=0, sticky=tk.W, pady=2)
        mode_combo = ttk.Combobox(frame, textvariable=self.processing_mode, 
                                values=["concat_fast", "encode_aac", "final_m4b"], 
                                state="readonly", width=20)
        mode_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Bitrate
        ttk.Label(frame, text="Bitrate:").grid(row=1, column=0, sticky=tk.W, pady=2)
        bitrate_combo = ttk.Combobox(frame, textvariable=self.audio_bitrate,
                                   values=["64k", "96k", "128k", "192k", "256k"],
                                   state="readonly", width=20)
        bitrate_combo.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Sample rate
        ttk.Label(frame, text="Sample Rate:").grid(row=2, column=0, sticky=tk.W, pady=2)
        sr_combo = ttk.Combobox(frame, textvariable=self.sample_rate,
                               values=[22050, 44100, 48000, 96000],
                               state="readonly", width=20)
        sr_combo.grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Options GPU et Loudnorm
        ttk.Checkbutton(frame, text="Activer GPU", variable=self.enable_gpu).grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Checkbutton(frame, text="Normalisation Loudnorm", variable=self.enable_loudnorm).grid(row=3, column=1, sticky=tk.W, pady=5)
        
    def create_control_section(self, parent):
        """Section des contrôles"""
        frame = ttk.Frame(parent)
        frame.grid(row=3, column=0, columnspan=3, pady=(0, 10))
        
        # Boutons principaux
        ttk.Button(frame, text="🚀 Lancer Conversion", 
                 command=self.start_conversion).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(frame, text="⏸️ Pause", 
                 command=self.pause_conversion).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(frame, text="⏹️ Arrêter", 
                 command=self.stop_conversion).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(frame, text="📁 Ouvrir Sortie", 
                 command=self.open_output).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(frame, text="⚙️ Config", 
                 command=self.open_config).pack(side=tk.LEFT, padx=5)
        
    def create_progress_section(self, parent):
        """Section de progression"""
        frame = ttk.LabelFrame(parent, text="📊 Progression", padding="10")
        frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(2, weight=1)
        
        # Status
        ttk.Label(frame, text="Status:", style='Header.TLabel').grid(row=0, column=0, sticky=tk.W)
        status_label = ttk.Label(frame, textvariable=self.status_var, style='Success.TLabel')
        status_label.grid(row=0, column=1, sticky=tk.W, padx=10)
        
        # Fichier actuel
        ttk.Label(frame, text="Fichier actuel:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        current_file_label = ttk.Label(frame, textvariable=self.current_file_var)
        current_file_label.grid(row=1, column=1, sticky=tk.W, padx=10, pady=(5, 0))
        
        # Barre de progression
        ttk.Label(frame, text="Progression:").grid(row=2, column=0, sticky=tk.NW, pady=(5, 0))
        progress_bar = ttk.Progressbar(frame, variable=self.progress_var, maximum=100, length=400)
        progress_bar.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=10, pady=(5, 0))
        
        # Pourcentage
        self.progress_label = ttk.Label(frame, text="0%")
        self.progress_label.grid(row=2, column=2, sticky=tk.W, pady=(5, 0))
        
    def create_log_section(self, parent):
        """Section des logs"""
        frame = ttk.LabelFrame(parent, text="📋 Logs", padding="10")
        frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        
        # Zone de logs
        self.log_text = scrolledtext.ScrolledText(frame, height=10, wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Boutons de log
        log_frame = ttk.Frame(frame)
        log_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        ttk.Button(log_frame, text="Effacer", command=self.clear_logs).pack(side=tk.LEFT, padx=5)
        ttk.Button(log_frame, text="Sauvegarder", command=self.save_logs).pack(side=tk.LEFT, padx=5)
        
    def browse_source(self):
        """Sélection du répertoire source"""
        directory = filedialog.askdirectory(title="Sélectionner le répertoire source")
        if directory:
            self.source_dir.set(directory)
            
    def browse_output(self):
        """Sélection du répertoire de sortie"""
        directory = filedialog.askdirectory(title="Sélectionner le répertoire de sortie")
        if directory:
            self.output_dir.set(directory)
            
    def start_conversion(self):
        """Démarrer la conversion"""
        if not self.source_dir.get() or not self.output_dir.get():
            messagebox.showerror("Erreur", "Veuillez sélectionner les répertoires source et sortie")
            return
            
        # Validation des répertoires
        if not os.path.exists(self.source_dir.get()):
            messagebox.showerror("Erreur", "Le répertoire source n'existe pas")
            return
            
        # Création du répertoire de sortie
        os.makedirs(self.output_dir.get(), exist_ok=True)
        
        # Démarrage dans un thread séparé
        thread = threading.Thread(target=self.run_conversion, daemon=True)
        thread.start()
        
        self.log("🚀 Démarrage de la conversion...")
        self.status_var.set("En cours")
        
    def run_conversion(self):
        """Exécution de la conversion dans un thread séparé"""
        try:
            # Configuration du processeur
            config = ProcessingConfig(
                source_directory=self.source_dir.get(),
                output_directory=self.output_dir.get(),
                processing_mode=self.processing_mode.get(),
                audio_bitrate=self.audio_bitrate.get(),
                sample_rate=self.sample_rate.get(),
                enable_gpu_acceleration=self.enable_gpu.get(),
                enable_loudnorm=self.enable_loudnorm.get()
            )
            
            processor = AudiobookProcessor(config)
            
            # Simulation de progression (à remplacer par la vraie logique)
            for i in range(101):
                self.queue.put(('progress', i))
                self.queue.put(('status', f'Traitement en cours... {i}%'))
                if i % 10 == 0:
                    self.queue.put(('log', f'🔄 Progression: {i}%'))
                threading.Event().wait(0.1)  # Simulation
                
            self.queue.put(('complete', 'Conversion terminée avec succès!'))
            
        except Exception as e:
            self.queue.put(('error', f'Erreur lors de la conversion: {str(e)}'))
            
    def pause_conversion(self):
        """Mettre en pause la conversion"""
        self.log("⏸️ Conversion mise en pause")
        self.status_var.set("En pause")
        
    def stop_conversion(self):
        """Arrêter la conversion"""
        self.log("⏹️ Conversion arrêtée")
        self.status_var.set("Arrêté")
        self.progress_var.set(0)
        
    def open_output(self):
        """Ouvrir le répertoire de sortie"""
        if self.output_dir.get() and os.path.exists(self.output_dir.get()):
            os.startfile(self.output_dir.get()) if sys.platform == "win32" else os.system(f'xdg-open "{self.output_dir.get()}"')
        else:
            messagebox.showwarning("Attention", "Le répertoire de sortie n'existe pas")
            
    def open_config(self):
        """Ouvrir la configuration avancée"""
        messagebox.showinfo("Configuration", "Configuration avancée à implémenter")
        
    def clear_logs(self):
        """Effacer les logs"""
        self.log_text.delete(1.0, tk.END)
        
    def save_logs(self):
        """Sauvegarder les logs"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".log",
            filetypes=[("Fichiers log", "*.log"), ("Tous les fichiers", "*.*")]
        )
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.log_text.get(1.0, tk.END))
            self.log(f"📄 Logs sauvegardés dans {filename}")
            
    def log(self, message):
        """Ajouter un message dans les logs"""
        self.queue.put(('log', message))
        
    def process_queue(self):
        """Traiter les messages de la queue"""
        try:
            while True:
                msg_type, message = self.queue.get_nowait()
                
                if msg_type == 'progress':
                    self.progress_var.set(message)
                    self.progress_label.config(text=f"{message}%")
                elif msg_type == 'status':
                    self.status_var.set(message)
                elif msg_type == 'log':
                    self.log_text.insert(tk.END, f"{message}\n")
                    self.log_text.see(tk.END)
                elif msg_type == 'complete':
                    self.status_var.set("Terminé")
                    self.progress_var.set(100)
                    self.log_text.insert(tk.END, f"✅ {message}\n")
                    self.log_text.see(tk.END)
                    messagebox.showinfo("Succès", message)
                elif msg_type == 'error':
                    self.status_var.set("Erreur")
                    self.log_text.insert(tk.END, f"❌ {message}\n")
                    self.log_text.see(tk.END)
                    messagebox.showerror("Erreur", message)
                    
        except queue.Empty:
            pass
            
        self.root.after(100, self.process_queue)

def main():
    """Point d'entrée principal"""
    root = tk.Tk()
    app = AudiobookManagerGUI(root)
    
    # Icône de l'application (si disponible)
    try:
        root.iconbitmap("icon.ico")
    except:
        pass
        
    root.mainloop()

if __name__ == "__main__":
    main()