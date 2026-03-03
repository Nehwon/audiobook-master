#!/usr/bin/env python3
"""
Interface web pour Audiobook Manager Pro
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire src au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from flask_socketio import SocketIO, emit
import logging
from datetime import datetime
import time
from pathlib import Path
from datetime import datetime
import subprocess
from audiobook_processor import AudiobookProcessor, AudiobookMetadata
from core.config import ProcessingConfig

app = Flask(__name__)
app.config['SECRET_KEY'] = 'audiobook_manager_2024'
socketio = SocketIO(app, cors_allowed_origins="*")

# Configuration
SOURCE_DIR = "/home/fabrice/Documents/Audiobooks"
OUTPUT_DIR = "/home/fabrice/Documents/Audiobooks_Processed"
TEMP_DIR = "/tmp/audiobooks_web"

# Variables globales
current_processor = None
conversion_status = {
    'status': 'idle',
    'progress': 0,
    'current_file': '',
    'total_files': 0,
    'processed_files': 0,
    'start_time': None,
    'estimated_time': None,
    'error': None
}

@app.route('/')
def index():
    """Page principale avec dashboard"""
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    """API pour obtenir le statut actuel"""
    return jsonify(conversion_status)

@app.route('/api/files')
def get_files():
    """API pour lister les fichiers disponibles"""
    source_path = Path(SOURCE_DIR)
    files = []
    
    if source_path.exists():
        for item in source_path.iterdir():
            if item.is_file() and item.suffix.lower() in ['.zip', '.rar', '.mp3', '.m4a', '.m4b']:
                files.append({
                    'name': item.name,
                    'size': item.stat().st_size,
                    'type': 'file',
                    'modified': item.stat().st_mtime
                })
            elif item.is_dir():
                # Compte les fichiers audio dans le dossier
                audio_count = len(list(item.rglob('*.mp3')) + list(item.rglob('*.m4a')))
                if audio_count > 0:
                    files.append({
                        'name': item.name,
                        'size': sum(f.stat().st_size for f in item.rglob('*') if f.is_file()),
                        'type': 'folder',
                        'audio_count': audio_count,
                        'modified': item.stat().st_mtime
                    })
    
    return jsonify(sorted(files, key=lambda x: x['name']))

@app.route('/api/outputs')
def get_outputs():
    """API pour lister les fichiers convertis"""
    output_path = Path(OUTPUT_DIR)
    files = []
    
    if output_path.exists():
        for item in output_path.glob('*.m4b'):
            files.append({
                'name': item.name,
                'size': item.stat().st_size,
                'created': item.stat().st_ctime,
                'path': str(item)
            })
    
    return jsonify(sorted(files, key=lambda x: x['created'], reverse=True))

@app.route('/api/convert', methods=['POST'])
def start_conversion():
    """API pour démarrer une conversion"""
    global current_processor, conversion_status
    
    data = request.json
    filename = data.get('filename')
    options = data.get('options', {})
    
    if not filename:
        return jsonify({'error': 'Nom de fichier requis'}), 400
    
    if conversion_status['status'] == 'processing':
        return jsonify({'error': 'Conversion déjà en cours'}), 400
    
    # Configuration
    config = ProcessingConfig()
    if 'bitrate' in options:
        config.audio_bitrate = options['bitrate']
    if 'samplerate' in options:
        config.sample_rate = options['samplerate']
    if 'no_gpu' in options and options['no_gpu']:
        config.enable_gpu_acceleration = False
    if 'no_normalization' in options and options['no_normalization']:
        config.enable_loudnorm = False
    if 'no_compression' in options and options['no_compression']:
        config.enable_compressor = False
    
    # Met à jour le statut
    conversion_status.update({
        'status': 'processing',
        'progress': 0,
        'current_file': filename,
        'total_files': 1,
        'processed_files': 0,
        'start_time': time.time(),
        'estimated_time': None,
        'error': None
    })
    
    # Démarre la conversion dans un thread séparé
    def conversion_thread():
        global current_processor
        try:
            current_processor = AudiobookProcessor(SOURCE_DIR, OUTPUT_DIR, TEMP_DIR)
            current_processor.config = config
            
            file_path = Path(SOURCE_DIR) / filename
            success = current_processor.process_audiobook(file_path)
            
            if success:
                conversion_status['status'] = 'completed'
                conversion_status['progress'] = 100
                socketio.emit('conversion_complete', {'filename': filename})
            else:
                conversion_status['status'] = 'error'
                conversion_status['error'] = 'Échec de la conversion'
                socketio.emit('conversion_error', {'error': 'Échec de la conversion'})
                
        except Exception as e:
            conversion_status['status'] = 'error'
            conversion_status['error'] = str(e)
            socketio.emit('conversion_error', {'error': str(e)})
        finally:
            current_processor = None
    
    thread = threading.Thread(target=conversion_thread)
    thread.daemon = True
    thread.start()
    
    return jsonify({'status': 'started'})

@app.route('/api/stop', methods=['POST'])
def stop_conversion():
    """API pour arrêter la conversion"""
    global current_processor, conversion_status
    
    if conversion_status['status'] != 'processing':
        return jsonify({'error': 'Aucune conversion en cours'}), 400
    
    # TODO: Implémenter l'arrêt propre du processus
    conversion_status['status'] = 'stopped'
    socketio.emit('conversion_stopped')
    
    return jsonify({'status': 'stopped'})

@app.route('/api/download/<filename>')
def download_file(filename):
    """API pour télécharger un fichier converti"""
    file_path = Path(OUTPUT_DIR) / filename
    if file_path.exists():
        return send_file(str(file_path), as_attachment=True)
    return jsonify({'error': 'Fichier non trouvé'}), 404

@app.route('/api/metadata/<filename>')
def get_metadata(filename):
    """API pour obtenir les métadonnées d'un fichier"""
    try:
        file_path = Path(SOURCE_DIR) / filename
        processor = AudiobookProcessor(SOURCE_DIR, OUTPUT_DIR, TEMP_DIR)
        metadata = processor.parse_filename(filename)
        
        return jsonify({
            'title': metadata.title,
            'author': metadata.author,
            'series': metadata.series,
            'series_number': metadata.series_number,
            'narrator': metadata.narrator,
            'year': metadata.year,
            'genre': metadata.genre
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@socketio.on('connect')
def handle_connect():
    """Gestion de la connexion WebSocket"""
    emit('status_update', conversion_status)

@socketio.on('disconnect')
def handle_disconnect():
    """Gestion de la déconnexion WebSocket"""
    pass

if __name__ == '__main__':
    # Crée les dossiers nécessaires
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    Path(TEMP_DIR).mkdir(parents=True, exist_ok=True)
    
    print("🚀 Démarrage de l'interface web...")
    print(f"📁 Source: {SOURCE_DIR}")
    print(f"📁 Sortie: {OUTPUT_DIR}")
    print("🌐 Interface disponible sur: http://localhost:5000")
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
