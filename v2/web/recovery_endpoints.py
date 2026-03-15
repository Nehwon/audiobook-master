#!/usr/bin/env python3

from flask import Blueprint, jsonify, request
from persistence.recovery_service import RecoveryService
from persistence.models import ProcessingJob, ProcessingJobStatus
from sqlalchemy.orm import Session

recovery_bp = Blueprint('recovery', __name__)
recovery_service = RecoveryService()

@recovery_bp.route('/api/recovery/status', methods=['GET'])
def get_recovery_status():
    """Endpoint pour obtenir l'état de la reprise automatique."""
    orphaned_jobs = recovery_service.detect_orphaned_jobs()
    
    return jsonify({
        "orphaned_job_count": len(orphaned_jobs),
        "status": "healthy" if not orphaned_jobs else "degraded",
        "jobs": [
            {
                "id": job.id,
                "status": job.status.value,
                "last_heartbeat": job.last_heartbeat.isoformat(),
                "retry_count": job.retry_count
            }
            for job in orphaned_jobs
        ]
    })

@recovery_bp.route('/api/recovery/process', methods=['POST'])
def process_orphaned_jobs():
    """Endpoint pour déclencher le traitement des jobs orphelins."""
    retry_policy = request.json.get('retry_policy', 'safe_retry')
    success_count = recovery_service.process_orphaned_jobs(retry_policy)
    
    return jsonify({
        "success": success_count,
        "message": f"{success_count} jobs traités avec succès"
    })

@recovery_bp.route('/api/jobs/<int:job_id>/heartbeat', methods=['POST'])
def update_job_heartbeat(job_id):
    """Endpoint pour mettre à jour le heartbeat d'un job."""
    success = recovery_service.update_job_heartbeat(job_id)
    
    if success:
        return jsonify({
            "success": True,
            "message": f"Heartbeat mis à jour pour le job {job_id}"
        }), 200
    else:
        return jsonify({
            "success": False,
            "message": f"Échec de la mise à jour du heartbeat pour le job {job_id}"
        }), 404
