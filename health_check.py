# 🐳 Docker Health Check Endpoint

from flask import Flask, jsonify
import psutil
import os
from datetime import datetime

app = Flask(__name__)

@app.route('/health')
def health_check():
    """Endpoint de santé pour les conteneurs et monitoring"""
    try:
        # Vérification de base
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': os.getenv('VERSION', '2.1.0'),
            'service': 'audiobook-manager-pro'
        }
        
        # Vérification des ressources système
        health_status['system'] = {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage': {
                'percent': psutil.disk_usage('/').percent
            }
        }
        
        # Vérification des dépendances critiques
        try:
            import mutagen
            health_status['dependencies'] = {
                'mutagen': 'available'
            }
        except ImportError:
            health_status['dependencies'] = {
                'mutagen': 'missing'
            }
            health_status['status'] = 'degraded'
            
        try:
            import requests
            health_status['dependencies']['requests'] = 'available'
        except ImportError:
            health_status['dependencies']['requests'] = 'missing'
            health_status['status'] = 'degraded'
            
        # Vérification des répertoires
        required_dirs = ['/app/data/source', '/app/data/output', '/app/temp']
        health_status['directories'] = {}
        
        for dir_path in required_dirs:
            if os.path.exists(dir_path):
                health_status['directories'][dir_path] = 'accessible'
            else:
                health_status['directories'][dir_path] = 'missing'
                health_status['status'] = 'degraded'
                
        return jsonify(health_status), 200
        
    except Exception as e:
        error_response = {
            'status': 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e),
            'service': 'audiobook-manager-pro'
        }
        return jsonify(error_response), 503

@app.route('/api/status')
def api_status():
    """Endpoint de statut détaillé pour l'API"""
    try:
        return jsonify({
            'api': 'operational',
            'version': os.getenv('VERSION', '2.1.0'),
            'uptime': psutil.boot_time(),
            'processes': len(psutil.pids()),
            'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else None,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({
            'api': 'error',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@app.route('/')
def index():
    """Page d'accueil simple"""
    return jsonify({
        'service': 'Audiobook Manager Pro',
        'version': os.getenv('VERSION', '2.1.0'),
        'status': 'running',
        'endpoints': {
            'health': '/health',
            'api_status': '/api/status',
            'docs': '/docs'
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)