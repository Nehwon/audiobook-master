from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import FolderState, OutboxEvent, ProcessingError, ProcessingJob


class ProcessingJobRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, *, job_id: str, folder_id: str, status: str = "queued") -> ProcessingJob:
        job = ProcessingJob(id=job_id, folder_id=folder_id, status=status)
        self.session.add(job)
        return job

    def get(self, job_id: str) -> Optional[ProcessingJob]:
        return self.session.get(ProcessingJob, job_id)

    def set_status(self, job_id: str, status: str) -> ProcessingJob:
        job = self.get(job_id)
        if job is None:
            raise ValueError(f"Unknown job_id: {job_id}")
        job.status = status
        return job


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
