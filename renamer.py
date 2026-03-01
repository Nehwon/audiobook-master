#!/usr/bin/env python3
"""
Étape de renommage préalable pour normaliser les noms de fichiers et dossiers
- Remplace les + par des espaces
- Remplace les ' par des _
- Nettoie les caractères problématiques
"""

import os
import re
from pathlib import Path
import shutil

class AudiobookRenamer:
    def __init__(self, source_dir="Test"):
        self.source_dir = Path(source_dir)
        self.renamed_files = []
        self.renamed_dirs = []
    
    def clean_filename(self, filename):
        """Nettoie un nom de fichier"""
        # Remplace les + par des espaces
        cleaned = filename.replace('+', ' ')
        
        # Remplace les ' par des _
        cleaned = cleaned.replace("'", "_")
        
        # Remplace les caractères problématiques
        cleaned = re.sub(r'[<>:"/\\|?*]', '_', cleaned)
        
        # Nettoie les espaces multiples
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned
    
    def rename_files_recursively(self, directory):
        """Renomme les fichiers récursivement"""
        directory = Path(directory)
        
        # D'abord renomme les fichiers
        for file_path in directory.rglob("*"):
            if file_path.is_file():
                old_name = file_path.name
                new_name = self.clean_filename(old_name)
                
                if new_name != old_name:
                    new_path = file_path.parent / new_name
                    
                    # Vérifie si le nouveau nom n'existe pas déjà
                    if not new_path.exists():
                        try:
                            file_path.rename(new_path)
                            self.renamed_files.append((str(file_path), str(new_path)))
                            print(f"📄 Fichier: {old_name} → {new_name}")
                        except Exception as e:
                            print(f"❌ Erreur renommage fichier {old_name}: {e}")
    
    def rename_directories(self):
        """Renomme les dossiers"""
        # Traite les dossiers du plus profond au moins profond
        dirs = sorted([d for d in self.source_dir.rglob("*") if d.is_dir()], 
                     key=lambda x: len(x.parts), reverse=True)
        
        for dir_path in dirs:
            old_name = dir_path.name
            new_name = self.clean_filename(old_name)
            
            if new_name != old_name:
                new_path = dir_path.parent / new_name
                
                # Vérifie si le nouveau nom n'existe pas déjà
                if not new_path.exists():
                    try:
                        dir_path.rename(new_path)
                        self.renamed_dirs.append((str(dir_path), str(new_path)))
                        print(f"📁 Dossier: {old_name} → {new_name}")
                    except Exception as e:
                        print(f"❌ Erreur renommage dossier {old_name}: {e}")
    
    def create_backup(self):
        """Crée un backup de la structure actuelle"""
        backup_dir = Path(f"{self.source_dir}_backup")
        if backup_dir.exists():
            shutil.rmtree(backup_dir)
        
        print(f"📦 Création du backup dans: {backup_dir}")
        shutil.copytree(self.source_dir, backup_dir)
        
        return backup_dir
    
    def run_renaming(self, create_backup=True):
        """Lance le processus de renommage"""
        print("🔧 RENOMMAGE DES AUDIOBOOKS")
        print("=" * 50)
        
        if create_backup:
            backup_dir = self.create_backup()
            print(f"✅ Backup créé: {backup_dir}")
        
        print(f"\n📂 Traitement du dossier: {self.source_dir}")
        
        # D'abord renomme les fichiers
        print("\n📄 Renommage des fichiers...")
        self.rename_files_recursively(self.source_dir)
        
        # Ensuite renomme les dossiers
        print("\n📁 Renommage des dossiers...")
        self.rename_directories()
        
        # Affiche le résumé
        self.print_summary()
    
    def print_summary(self):
        """Affiche le résumé des renommages"""
        print("\n" + "=" * 50)
        print("📊 RÉSUMÉ DU RENOMMAGE")
        print("=" * 50)
        
        print(f"\n📁 Dossiers renommés: {len(self.renamed_dirs)}")
        for old, new in self.renamed_dirs[:5]:  # Affiche les 5 premiers
            print(f"   {old} → {new}")
        if len(self.renamed_dirs) > 5:
            print(f"   ... et {len(self.renamed_dirs) - 5} autres")
        
        print(f"\n📄 Fichiers renommés: {len(self.renamed_files)}")
        for old, new in self.renamed_files[:5]:  # Affiche les 5 premiers
            print(f"   {old} → {new}")
        if len(self.renamed_files) > 5:
            print(f"   ... et {len(self.renamed_files) - 5} autres")
        
        print(f"\n✅ Renommage terminé !")
        print(f"💡 Les noms sont maintenant compatibles avec le traitement audio")
    
    def save_log(self):
        """Sauvegarde le log des renommages"""
        log_file = Path("renaming_log.txt")
        
        with open(log_file, 'w') as f:
            f.write("LOG DE RENOMMAGE DES AUDIOBOOKS\n")
            f.write("=" * 50 + "\n\n")
            
            f.write("DOSSIERS RENOMMÉS:\n")
            for old, new in self.renamed_dirs:
                f.write(f"{old} → {new}\n")
            
            f.write("\nFICHIERS RENOMMÉS:\n")
            for old, new in self.renamed_files:
                f.write(f"{old} → {new}\n")
        
        print(f"\n📝 Log sauvegardé dans: {log_file}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Renomme les fichiers et dossiers d'audiobooks")
    parser.add_argument("--source", default="Test", help="Dossier source à traiter")
    parser.add_argument("--no-backup", action="store_true", help="Ne pas créer de backup")
    
    args = parser.parse_args()
    
    renamer = AudiobookRenamer(args.source)
    renamer.run_renaming(create_backup=not args.no_backup)
    renamer.save_log()
