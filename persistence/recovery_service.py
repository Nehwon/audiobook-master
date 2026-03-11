#!/usr/bin/env python3

import logging
from datetime import datetime, timedelta
from typing import List, Optional

from persistence.db import get_db_session
from persistence.models import ProcessingJob, ProcessingJobStatus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RecoveryService:
    def __init__(self, heartbeat_timeout_minutes: int = 5):
        self.heartbeat_timeout = timedelta(minutes=heartbeat_timeout_minutes)

    def detect_orphaned_jobs(self) -> List[ProcessingJob]:
        """Détecte les jobs 'running' orphelins sans heartbeat récent."""
        session = get_db_session()
        cutoff_time = datetime.utcnow() - self.heartbeat_timeout
        
        orphaned_jobs = session.query(ProcessingJob)\n            .filter(ProcessingJob.status == ProcessingJobStatus.RUNNING)\n            .filter(ProcessingJob.last_heartbeat < cutoff_time)\n            .all()
        
        logger.info(f"Détecté {len(orphaned_jobs)} jobs orphelins")
        return orphaned_jobs

    def handle_orphaned_job(self, job: ProcessingJob, retry_policy: str = "safe_retry") -> bool:
        """Traite un job orphelin selon la politique de retry."""
        session = get_db_session()
        
        if retry_policy == "safe_retry":
            job.status = ProcessingJobStatus.RETRY_PENDING
            job.retry_count += 1
            logger.info(f"Job {job.id} marqué pour retry safe")
        elif retry_policy == "manual_intervention":
            job.status = ProcessingJobStatus.FAILED
            job.error_text = "Job orphelin - intervention manuelle requise"
            logger.warning(f"Job {job.id} nécessite intervention manuelle")
        else:
            logger.error(f"Politique de retry inconnue: {retry_policy}")
            return False
        
        session.commit()
        return True

    def process_orphaned_jobs(self, retry_policy: str = "safe_retry") -> int:
        """Traite tous les jobs orphelins détectés."""
        orphaned_jobs = self.detect_orphaned_jobs()
        success_count = 0
        
        for job in orphaned_jobs:
            if self.handle_orphaned_job(job, retry_policy):
                success_count += 1
        
        logger.info(f"Traitement des jobs orphelins terminé. Succès: {success_count}/{len(orphaned_jobs)}")
        return success_count

    def update_job_heartbeat(self, job_id: int) -> bool:
        """Met à jour le heartbeat d'un job actif."""
        session = get_db_session()
        job = session.query(ProcessingJob).get(job_id)
        
        if not job:
            logger.error(f"Job {job_id} non trouvé")
            return False
        
        job.last_heartbeat = datetime.utcnow()
        session.commit()
        return True

if __name__ == "__main__":
    recovery_service = RecoveryService()
    recovery_service.process_orphaned_jobs()
