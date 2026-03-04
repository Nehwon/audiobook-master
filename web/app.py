#!/usr/bin/env python3
"""Interface web pour Audiobook Manager Pro."""

import os
import threading
import time
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_file
from flask_socketio import SocketIO, emit

from core.config import ProcessingConfig
from core.processor import AudiobookProcessor

app = Flask(__name__)
app.config['SECRET_KEY'] = 'audiobook_manager_2024'
socketio = SocketIO(app, cors_allowed_origins="*")

# Configuration (surchageable par variables d'environnement)
SOURCE_DIR = os.getenv("AUDIOBOOK_SOURCE_DIR", "/home/fabrice/Documents/Audiobooks")
OUTPUT_DIR = os.getenv("AUDIOBOOK_OUTPUT_DIR", "/home/fabrice/Documents/Audiobooks_Processed")
TEMP_DIR = os.getenv("AUDIOBOOK_TEMP_DIR", "/tmp/audiobooks_web")

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
    'error': None,
}


def _count_audio_files(folder: Path) -> int:
    audio_extensions = ("*.mp3", "*.m4a", "*.m4b", "*.wav", "*.flac", "*.aac")
    return sum(len(list(folder.rglob(pattern))) for pattern in audio_extensions)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/status')
def get_status():
    return jsonify(conversion_status)


@app.route('/api/folders')
def get_folders():
    """Liste les dossiers source qui contiennent des fichiers audio."""
    source_path = Path(SOURCE_DIR)
    folders = []

    if source_path.exists():
        for item in sorted(source_path.iterdir(), key=lambda p: p.name.lower()):
            if not item.is_dir():
                continue
            audio_count = _count_audio_files(item)
            if audio_count <= 0:
                continue

            folder_size = sum(f.stat().st_size for f in item.rglob('*') if f.is_file())
            folders.append(
                {
                    'name': item.name,
                    'audio_count': audio_count,
                    'size': folder_size,
                    'modified': item.stat().st_mtime,
                }
            )

    return jsonify(folders)


@app.route('/api/outputs')
def get_outputs():
    output_path = Path(OUTPUT_DIR)
    files = []

    if output_path.exists():
        for item in output_path.glob('*.m4b'):
            files.append(
                {
                    'name': item.name,
                    'size': item.stat().st_size,
                    'created': item.stat().st_ctime,
                }
            )

    return jsonify(sorted(files, key=lambda x: x['created'], reverse=True))


@app.route('/api/convert', methods=['POST'])
def start_conversion():
    """Lance l'encodage d'un dossier (ou d'un fichier) en M4B."""
    global current_processor, conversion_status

    data = request.get_json(silent=True) or {}
    folder_name = data.get('folder') or data.get('filename')
    options = data.get('options', {})

    if not folder_name:
        return jsonify({'error': 'Nom de dossier requis'}), 400
    if conversion_status['status'] == 'processing':
        return jsonify({'error': 'Conversion déjà en cours'}), 400

    source_item = Path(SOURCE_DIR) / folder_name
    if not source_item.exists():
        return jsonify({'error': f'Dossier introuvable: {folder_name}'}), 404

    config = ProcessingConfig()
    if 'bitrate' in options:
        config.audio_bitrate = options['bitrate']
    if 'samplerate' in options:
        config.sample_rate = options['samplerate']
    if options.get('no_gpu'):
        config.enable_gpu_acceleration = False
    if options.get('no_normalization'):
        config.enable_loudnorm = False
    if options.get('no_compression'):
        config.enable_compressor = False
    if 'processing_mode' in options:
        config.processing_mode = options['processing_mode']

    conversion_status.update(
        {
            'status': 'processing',
            'progress': 0,
            'current_file': folder_name,
            'total_files': 1,
            'processed_files': 0,
            'start_time': time.time(),
            'estimated_time': None,
            'error': None,
        }
    )
    socketio.emit('status_update', conversion_status)

    def conversion_thread():
        global current_processor, conversion_status
        try:
            current_processor = AudiobookProcessor(SOURCE_DIR, OUTPUT_DIR, TEMP_DIR)
            current_processor.config = config

            success = current_processor.process_audiobook(source_item)

            if success:
                conversion_status['status'] = 'completed'
                conversion_status['progress'] = 100
                conversion_status['processed_files'] = 1
                socketio.emit('conversion_complete', {'folder': folder_name})
            else:
                conversion_status['status'] = 'error'
                conversion_status['error'] = 'Échec de la conversion'
                socketio.emit('conversion_error', {'error': 'Échec de la conversion'})
        except Exception as exc:
            conversion_status['status'] = 'error'
            conversion_status['error'] = str(exc)
            socketio.emit('conversion_error', {'error': str(exc)})
        finally:
            current_processor = None
            socketio.emit('status_update', conversion_status)

    thread = threading.Thread(target=conversion_thread, daemon=True)
    thread.start()
    return jsonify({'status': 'started'})


@app.route('/api/stop', methods=['POST'])
def stop_conversion():
    global conversion_status

    if conversion_status['status'] != 'processing':
        return jsonify({'error': 'Aucune conversion en cours'}), 400

    conversion_status['status'] = 'stopped'
    socketio.emit('conversion_stopped')
    socketio.emit('status_update', conversion_status)
    return jsonify({'status': 'stopped'})


@app.route('/api/download/<filename>')
def download_file(filename):
    file_path = Path(OUTPUT_DIR) / filename
    if file_path.exists():
        return send_file(str(file_path), as_attachment=True)
    return jsonify({'error': 'Fichier non trouvé'}), 404


@socketio.on('connect')
def handle_connect():
    emit('status_update', conversion_status)


if __name__ == '__main__':
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    Path(TEMP_DIR).mkdir(parents=True, exist_ok=True)
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
