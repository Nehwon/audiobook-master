#!/usr/bin/env python3
"""
📦 Script de Packaging Multi-Plateforme - Audiobook Manager Pro
Création des exécutables pour Windows, Linux et macOS
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import argparse

class PackageBuilder:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.dist_dir = self.project_root / "dist"
        self.build_dir = self.project_root / "build"
        
    def clean(self):
        """Nettoyer les répertoires de build"""
        print("🧹 Nettoyage des répertoires de build...")
        
        for dir_path in [self.dist_dir, self.build_dir]:
            if dir_path.exists():
                shutil.rmtree(dir_path)
                print(f"✅ {dir_path} supprimé")
                
        # Création des répertoires
        self.dist_dir.mkdir(exist_ok=True)
        self.build_dir.mkdir(exist_ok=True)
        
    def create_requirements_txt(self):
        """Créer le fichier requirements.txt pour le packaging"""
        print("📝 Création du fichier requirements.txt...")
        
        requirements = """tkinter  # Inclus dans Python standard
flask==2.3.3
mutagen==1.47.0
requests==2.31.0
pydub==0.25.1
python-dotenv==1.0.0
gunicorn==21.2.0
"""
        
        req_file = self.project_root / "requirements-packaged.txt"
        with open(req_file, 'w') as f:
            f.write(requirements)
        print(f"✅ {req_file} créé")
        
    def create_pyinstaller_spec(self):
        """Créer le fichier spec pour PyInstaller"""
        print("📝 Création du fichier PyInstaller spec...")
        
        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['gui/desktop_app.py'],
    pathex=['{self.project_root}'],
    binaries=[],
    datas=[
        ('core', 'core'),
        ('web', 'web'),
        ('templates', 'templates'),
        ('docs', 'docs'),
        ('requirements-packaged.txt', '.'),
    ],
    hiddenimports=['tkinter', 'tkinter.ttk', 'tkinter.scrolledtext'],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AudiobookManagerPro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='gui/icon.ico' if os.path.exists('gui/icon.ico') else None,
)
'''
        
        spec_file = self.project_root / "audiobook-manager.spec"
        with open(spec_file, 'w') as f:
            f.write(spec_content)
        print(f"✅ {spec_file} créé")
        
    def create_windows_installer(self):
        """Créer l'installateur Windows avec NSIS"""
        print("🪟 Création de l'installateur Windows...")
        
        nsis_script = f'''
!define APPNAME "Audiobook Manager Pro"
!define VERSION "2.0.0"
!define PUBLISHER "Fabrice"
!define URL "https://github.com/fabrice-audiobook/audiobooks-manager"

!include "MUI2.nsh"

Name "${{APPNAME}}"
OutFile "AudiobookManagerPro-Setup-${{VERSION}}.exe"
InstallDir "$PROGRAMFILES64\\${{APPNAME}}"
InstallDirRegKey "HKCU\\Software\\${{APPNAME}}" "InstallPath"
RequestExecutionLevel admin

Page directory
Page instfiles

Section "MainSection" SEC01
    SetOutPath "$INSTDIR"
    File /r "dist\\AudiobookManagerPro\\*"
    
    CreateDirectory "$SMPROGRAMS\\${{APPNAME}}"
    CreateShortCut "$SMPROGRAMS\\${{APPNAME}}\\${{APPNAME}}.lnk" "$INSTDIR\\AudiobookManagerPro.exe"
    CreateShortCut "$SMPROGRAMS\\${{APPNAME}}\\Uninstall.lnk" "$INSTDIR\\Uninstall.exe"
    
    WriteRegStr HKCU "Software\\${{APPNAME}}" "InstallPath" "$INSTDIR"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "DisplayName" "${{APPNAME}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "UninstallString" "$INSTDIR\\Uninstall.exe"
    
    WriteUninstaller "$INSTDIR\\Uninstall.exe"
SectionEnd

Section "Uninstall"
    Delete "$INSTDIR\\Uninstall.exe"
    RMDir /r "$INSTDIR"
    Delete "$SMPROGRAMS\\${{APPNAME}}\\*.*"
    RMDir "$SMPROGRAMS\\${{APPNAME}}"
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}"
    DeleteRegKey HKCU "Software\\${{APPNAME}}"
SectionEnd
'''
        
        nsis_file = self.build_dir / "installer.nsi"
        with open(nsis_file, 'w') as f:
            f.write(nsis_script)
            
        # Compilation avec NSIS (si disponible)
        try:
            subprocess.run(['makensis', str(nsis_file)], check=True)
            print("✅ Installateur Windows créé")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️ NSIS non trouvé. Installateur Windows non créé")
            print("📥 Installez NSIS: https://nsis.sourceforge.io/")
            
    def create_linux_appimage(self):
        """Créer un AppImage Linux"""
        print("🐧 Création de l'AppImage Linux...")
        
        appdir = self.build_dir / "AudiobookManagerPro.AppDir"
        appdir.mkdir(exist_ok=True)
        
        # Structure AppImage
        (appdir / "usr" / "bin").mkdir(parents=True, exist_ok=True)
        (appdir / "usr" / "share" / "applications").mkdir(parents=True, exist_ok=True)
        (appdir / "usr" / "share" / "icons" / "hicolor" / "256x256" / "apps").mkdir(parents=True, exist_ok=True)
        
        # Copie des fichiers
        exe_path = self.dist_dir / "AudiobookManagerPro" / "AudiobookManagerPro"
        if exe_path.exists():
            shutil.copy2(exe_path, appdir / "usr" / "bin" / "AudiobookManagerPro")
            
        # Fichier .desktop
        desktop_content = '''[Desktop Entry]
Type=Application
Name=Audiobook Manager Pro
Comment=Système de traitement d'audiobooks avec multithreading CPU optimisé
Exec=AudiobookManagerPro
Icon=audiobook-manager-pro
Categories=AudioVideo;Audio;
'''
        with open(appdir / "usr" / "share" / "applications" / "audiobook-manager-pro.desktop", 'w') as f:
            f.write(desktop_content)
            
        # AppImage (requiert appimagetool)
        try:
            subprocess.run([
                'appimagetool', 
                str(appdir)
            ], check=True)
            print("✅ AppImage Linux créé")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️ appimagetool non trouvé. AppImage non créé")
            print("📥 Installez appimagetool: https://github.com/AppImage/appimagetool")
            
    def create_macos_bundle(self):
        """Créer un bundle macOS"""
        print("🍎 Création du bundle macOS...")
        
        app_dir = self.build_dir / "AudiobookManagerPro.app"
        contents_dir = app_dir / "Contents"
        
        # Structure du bundle
        (contents_dir / "MacOS").mkdir(parents=True, exist_ok=True)
        (contents_dir / "Resources").mkdir(exist_ok=True)
        
        # Copie de l'exécutable
        exe_path = self.dist_dir / "AudiobookManagerPro" / "AudiobookManagerPro"
        if exe_path.exists():
            shutil.copy2(exe_path, contents_dir / "MacOS" / "AudiobookManagerPro")
            
        # Info.plist
        info_plist = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>AudiobookManagerPro</string>
    <key>CFBundleIdentifier</key>
    <string>com.fabrice.audiobookmanagerpro</string>
    <key>CFBundleName</key>
    <string>Audiobook Manager Pro</string>
    <key>CFBundleVersion</key>
    <string>2.0.0</string>
    <key>CFBundleShortVersionString</key>
    <string>2.0.0</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleSignature</key>
    <string>????</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.14</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>LSApplicationCategoryType</key>
    <string>public.app-category.utilities</string>
</dict>
</plist>
'''
        
        with open(contents_dir / "Info.plist", 'w') as f:
            f.write(info_plist)
            
        print("✅ Bundle macOS créé")
        
    def build_executable(self):
        """Construire l'exécutable avec PyInstaller"""
        print("🔨 Construction de l'exécutable...")
        
        try:
            subprocess.run([
                'pyinstaller',
                '--clean',
                '--noconfirm',
                str(self.project_root / "audiobook-manager.spec")
            ], check=True)
            print("✅ Exécutable créé avec PyInstaller")
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur PyInstaller: {e}")
            return False
        except FileNotFoundError:
            print("❌ PyInstaller non trouvé")
            print("📥 Installez PyInstaller: pip install pyinstaller")
            return False
            
        return True
        
    def build_all(self):
        """Construire pour toutes les plateformes"""
        print("🚀 Construction multi-plateforme...")
        
        # Nettoyage
        self.clean()
        
        # Préparation
        self.create_requirements_txt()
        self.create_pyinstaller_spec()
        
        # Construction de l'exécutable
        if not self.build_executable():
            return
            
        # Création des packages spécifiques
        current_platform = sys.platform
        
        if current_platform == "win32":
            self.create_windows_installer()
        elif current_platform == "linux":
            self.create_linux_appimage()
        elif current_platform == "darwin":
            self.create_macos_bundle()
        else:
            print(f"⚠️ Plateforme non supportée: {current_platform}")
            
        print("✅ Construction terminée!")
        print(f"📁 Fichiers créés dans: {self.dist_dir}")

def main():
    parser = argparse.ArgumentParser(description="Packaging multi-plateforme pour Audiobook Manager Pro")
    parser.add_argument('--clean', action='store_true', help='Nettoyer les répertoires de build')
    parser.add_argument('--build', action='store_true', help='Construire l\'exécutable')
    parser.add_argument('--all', action='store_true', help='Construire pour toutes les plateformes')
    
    args = parser.parse_args()
    
    builder = PackageBuilder()
    
    if args.clean:
        builder.clean()
    elif args.build:
        builder.build_executable()
    elif args.all:
        builder.build_all()
    else:
        builder.build_all()

if __name__ == "__main__":
    main()