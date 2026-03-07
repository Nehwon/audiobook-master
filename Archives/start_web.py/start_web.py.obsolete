#!/usr/bin/env python3
"""
Lanceur de l'interface web pour Audiobook Manager Pro
Gère la nouvelle structure src/ et logs/
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire src au PYTHONPATH
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

def main():
    """Lance l'interface web"""
    import logging
    
    # Configuration du logging vers logs/
    log_file = Path(__file__).parent / "logs" / "web_ui.log"
    log_file.parent.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    
    try:
        # Importer et lancer l'interface web
        from web_ui import app, socketio
        
        logger.info("🌐 Démarrage de l'interface web...")
        logger.info("📍 Accès: http://localhost:5000")
        logger.info("📁 Logs: logs/web_ui.log")
        
        # Lancer le serveur Flask
        socketio.run(app, host='0.0.0.0', port=5000, debug=False)
        
    except KeyboardInterrupt:
        logger.info("⏹️ Arrêt de l'interface web")
    except Exception as e:
        logger.error(f"❌ Erreur lors du démarrage: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
