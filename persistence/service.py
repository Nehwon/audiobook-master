from __future__ import annotations

from sqlalchemy.orm import Session

from .repositories import (
    FolderStateRepository,
    OutboxEventRepository,
    ProcessingErrorRepository,
    ProcessingJobRepository,
)

ALLOWED_STATUSES = {"queued", "running", "failed", "done", "cancelled"}


class ProcessingStateService:
    """Transactional service used by workers to persist job transitions and errors."""

    def __init__(self, session: Session) -> None:
        self.jobs = ProcessingJobRepository(session)
        self.folders = FolderStateRepository(session)
        self.errors = ProcessingErrorRepository(session)
        self.events = OutboxEventRepository(session)

    def create_job(self, *, job_id: str, folder_id: str) -> None:
        self.jobs.create(job_id=job_id, folder_id=folder_id, status="queued")
        self.folders.upsert(folder_id=folder_id, status="queued", last_job_id=job_id)
        self.events.enqueue(
            aggregate_type="job",
            aggregate_id=job_id,
            event_type="job.queued",
            payload={"job_id": job_id, "folder_id": folder_id, "status": "queued"},
        )

    def transition_job(self, *, job_id: str, folder_id: str, status: str) -> None:
        if status not in ALLOWED_STATUSES:
            raise ValueError(f"Unsupported status: {status}")
        self.jobs.set_status(job_id, status)
        self.folders.upsert(folder_id=folder_id, status=status, last_job_id=job_id)
        self.events.enqueue(
            aggregate_type="job",
            aggregate_id=job_id,
            event_type="job.updated",
            payload={"job_id": job_id, "folder_id": folder_id, "status": status},
        )

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
