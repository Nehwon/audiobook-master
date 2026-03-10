from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from .repositories import (
    FolderStateRepository,
    OutboxEventRepository,
    ProcessingErrorRepository,
    ProcessingJobRepository,
    RecoveryAuditRepository,
)

ALLOWED_STATUSES = {"queued", "running", "failed", "done", "cancelled", "retry_pending"}


class ProcessingStateService:
    """Transactional service used by workers to persist job transitions and errors."""

    def __init__(self, session: Session) -> None:
        self.jobs = ProcessingJobRepository(session)
        self.folders = FolderStateRepository(session)
        self.errors = ProcessingErrorRepository(session)
        self.events = OutboxEventRepository(session)

    def create_job(self, *, job_id: str, folder_id: str, idempotency_key: str | None = None) -> None:
        if idempotency_key:
            existing_active_job = self.jobs.get_active_by_idempotency_key(idempotency_key)
            if existing_active_job is not None:
                raise ValueError(f"Duplicate active job for idempotency_key: {idempotency_key}")
        self.jobs.create(job_id=job_id, folder_id=folder_id, status="queued", idempotency_key=idempotency_key)
        self.folders.upsert(folder_id=folder_id, status="queued", last_job_id=job_id)
        self.events.enqueue(
            aggregate_type="job",
            aggregate_id=job_id,
            event_type="job.queued",
            payload={"job_id": job_id, "folder_id": folder_id, "status": "queued", "idempotency_key": idempotency_key},
        )

    def transition_job(self, *, job_id: str, folder_id: str, status: str, recovery_status: str | None = None) -> None:
        if status not in ALLOWED_STATUSES:
            raise ValueError(f"Unsupported status: {status}")
        self.jobs.set_status(job_id, status, recovery_status=recovery_status)
        self.folders.upsert(folder_id=folder_id, status=status, last_job_id=job_id)
        self.events.enqueue(
            aggregate_type="job",
            aggregate_id=job_id,
            event_type="job.updated",
            payload={"job_id": job_id, "folder_id": folder_id, "status": status, "recovery_status": recovery_status},
        )

    def touch_heartbeat(self, *, job_id: str, heartbeat_at: datetime | None = None) -> None:
        self.jobs.touch_heartbeat(job_id, at=heartbeat_at)

    def increment_retry_count(self, *, job_id: str) -> int:
        job = self.jobs.increment_retry_count(job_id)
        return int(job.retry_count)

    def record_error(
        self,
        *,
        job_id: str,
        folder_id: str,
        error_code: str,
        user_message: str,
        technical_message: str | None = None,
        stacktrace: str | None = None,
        retryable: bool = False,
    ) -> None:
        self.errors.add(
            job_id=job_id,
            folder_id=folder_id,
            error_code=error_code,
            user_message=user_message,
            technical_message=technical_message,
            stacktrace=stacktrace,
            retryable=retryable,
        )
        self.transition_job(job_id=job_id, folder_id=folder_id, status="failed")


class RecoveryService:
    def __init__(self, session: Session) -> None:
        self.jobs = ProcessingJobRepository(session)
        self.folders = FolderStateRepository(session)
        self.events = OutboxEventRepository(session)
        self.audit = RecoveryAuditRepository(session)

    def bootstrap_recovery(
        self,
        *,
        heartbeat_timeout_seconds: int = 300,
        max_retries: int = 3,
        now: datetime | None = None,
    ) -> dict[str, int]:
        orphans = self.jobs.list_orphan_running_jobs(heartbeat_timeout_seconds=heartbeat_timeout_seconds, now=now)
        summary = {"orphan_detected": len(orphans), "auto_retried": 0, "manual_intervention": 0}

        for job in orphans:
            if job.retry_count < max_retries:
                self.jobs.increment_retry_count(job.id)
                self.jobs.set_status(job.id, "retry_pending", recovery_status="auto_retried")
                self.folders.upsert(folder_id=job.folder_id, status="retry_pending", last_job_id=job.id)
                self.events.enqueue(
                    aggregate_type="job",
                    aggregate_id=job.id,
                    event_type="job.recovered",
                    payload={"job_id": job.id, "folder_id": job.folder_id, "status": "retry_pending", "decision": "auto_retried"},
                )
                self.audit.add(job_id=job.id, decision="auto_retried", reason="heartbeat_timeout")
                summary["auto_retried"] += 1
            else:
                self.jobs.set_status(job.id, "failed", recovery_status="manual_intervention")
                self.folders.upsert(folder_id=job.folder_id, status="failed", last_job_id=job.id)
                self.events.enqueue(
                    aggregate_type="job",
                    aggregate_id=job.id,
                    event_type="job.recovered",
                    payload={"job_id": job.id, "folder_id": job.folder_id, "status": "failed", "decision": "manual_intervention"},
                )
                self.audit.add(job_id=job.id, decision="manual_intervention", reason="max_retries_exceeded")
                summary["manual_intervention"] += 1
        return summary

    def get_recovery_status(self) -> dict[str, int]:
        return {
            "auto_retried": self.jobs.count_by_recovery_status("auto_retried"),
            "manual_intervention": self.jobs.count_by_recovery_status("manual_intervention"),
            "retry_pending": self.jobs.count_by_status("retry_pending"),
            "running": self.jobs.count_by_status("running"),
            "audit_auto_retried": self.audit.count_decisions("auto_retried"),
            "audit_manual_intervention": self.audit.count_decisions("manual_intervention"),
        }
