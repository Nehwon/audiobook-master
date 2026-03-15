from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .models import FolderState, OutboxEvent, ProcessingError, ProcessingJob, RecoveryAudit


ACTIVE_JOB_STATUSES = {"queued", "running", "retry_pending"}


class ProcessingJobRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, *, job_id: str, folder_id: str, status: str = "queued", idempotency_key: str | None = None) -> ProcessingJob:
        job = ProcessingJob(id=job_id, folder_id=folder_id, status=status, idempotency_key=idempotency_key)
        self.session.add(job)
        return job

    def get(self, job_id: str) -> Optional[ProcessingJob]:
        return self.session.get(ProcessingJob, job_id)

    def get_by_idempotency_key(self, idempotency_key: str) -> Optional[ProcessingJob]:
        stmt = select(ProcessingJob).where(ProcessingJob.idempotency_key == idempotency_key).limit(1)
        return self.session.scalars(stmt).first()

    def get_active_by_idempotency_key(self, idempotency_key: str) -> Optional[ProcessingJob]:
        stmt = select(ProcessingJob).where(
            ProcessingJob.idempotency_key == idempotency_key,
            ProcessingJob.status.in_(ACTIVE_JOB_STATUSES),
        ).limit(1)
        return self.session.scalars(stmt).first()

    def set_status(self, job_id: str, status: str, *, recovery_status: str | None = None) -> ProcessingJob:
        job = self.get(job_id)
        if job is None:
            raise ValueError(f"Unknown job_id: {job_id}")
        job.status = status
        if recovery_status is not None:
            job.recovery_status = recovery_status
        return job

    def touch_heartbeat(self, job_id: str, *, at: datetime | None = None) -> ProcessingJob:
        job = self.get(job_id)
        if job is None:
            raise ValueError(f"Unknown job_id: {job_id}")
        job.last_heartbeat_at = at or datetime.utcnow()
        return job

    def increment_retry_count(self, job_id: str) -> ProcessingJob:
        job = self.get(job_id)
        if job is None:
            raise ValueError(f"Unknown job_id: {job_id}")
        job.retry_count += 1
        return job

    def list_orphan_running_jobs(self, *, heartbeat_timeout_seconds: int, now: datetime | None = None) -> list[ProcessingJob]:
        current_time = now or datetime.utcnow()
        cutoff = current_time - timedelta(seconds=max(1, heartbeat_timeout_seconds))
        stmt = select(ProcessingJob).where(
            ProcessingJob.status == "running",
            (ProcessingJob.last_heartbeat_at.is_(None)) | (ProcessingJob.last_heartbeat_at < cutoff),
        )
        return list(self.session.scalars(stmt))

    def count_by_status(self, status: str) -> int:
        stmt = select(func.count()).select_from(ProcessingJob).where(ProcessingJob.status == status)
        return int(self.session.scalar(stmt) or 0)

    def count_by_recovery_status(self, recovery_status: str) -> int:
        stmt = select(func.count()).select_from(ProcessingJob).where(ProcessingJob.recovery_status == recovery_status)
        return int(self.session.scalar(stmt) or 0)


class FolderStateRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def upsert(self, *, folder_id: str, status: str, last_job_id: str | None = None) -> FolderState:
        folder_state = self.session.get(FolderState, folder_id)
        if folder_state is None:
            folder_state = FolderState(folder_id=folder_id, status=status, last_job_id=last_job_id)
            self.session.add(folder_state)
            return folder_state
        folder_state.status = status
        folder_state.last_job_id = last_job_id
        return folder_state


class ProcessingErrorRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, **payload) -> ProcessingError:
        error = ProcessingError(**payload)
        self.session.add(error)
        return error


class OutboxEventRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def enqueue(self, *, aggregate_type: str, aggregate_id: str, event_type: str, payload: dict) -> OutboxEvent:
        event = OutboxEvent(
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            event_type=event_type,
            payload=payload,
        )
        self.session.add(event)
        return event

    def list_pending(self, *, limit: int = 100) -> list[OutboxEvent]:
        stmt = select(OutboxEvent).order_by(OutboxEvent.id.asc()).limit(limit)
        return list(self.session.scalars(stmt))


class RecoveryAuditRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, *, job_id: str, decision: str, reason: str | None = None) -> RecoveryAudit:
        audit = RecoveryAudit(job_id=job_id, decision=decision, reason=reason)
        self.session.add(audit)
        return audit

    def count_decisions(self, decision: str) -> int:
        stmt = select(func.count()).select_from(RecoveryAudit).where(RecoveryAudit.decision == decision)
        return int(self.session.scalar(stmt) or 0)
