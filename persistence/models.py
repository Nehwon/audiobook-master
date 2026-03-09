from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class ProcessingJob(Base):
    __tablename__ = "processing_job"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    folder_id: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="queued")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    steps: Mapped[list[ProcessingStep]] = relationship(back_populates="job", cascade="all, delete-orphan")


class ProcessingStep(Base):
    __tablename__ = "processing_step"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[str] = mapped_column(ForeignKey("processing_job.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="queued")
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    details: Mapped[dict | None] = mapped_column(JSON)

    job: Mapped[ProcessingJob] = relationship(back_populates="steps")


class FolderState(Base):
    __tablename__ = "folder_state"

    folder_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    last_job_id: Mapped[str | None] = mapped_column(ForeignKey("processing_job.id", ondelete="SET NULL"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class ValidationResult(Base):
    __tablename__ = "validation_result"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    folder_id: Mapped[str] = mapped_column(String(255), nullable=False)
    validation_key: Mapped[str] = mapped_column(String(120), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    payload: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class ProcessingError(Base):
    __tablename__ = "processing_error"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[str | None] = mapped_column(ForeignKey("processing_job.id", ondelete="SET NULL"))
    folder_id: Mapped[str | None] = mapped_column(String(255))
    error_code: Mapped[str] = mapped_column(String(80), nullable=False)
    user_message: Mapped[str] = mapped_column(Text, nullable=False)
    technical_message: Mapped[str | None] = mapped_column(Text)
    stacktrace: Mapped[str | None] = mapped_column(Text)
    retryable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class OutboxEvent(Base):
    __tablename__ = "outbox_event"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    aggregate_type: Mapped[str] = mapped_column(String(64), nullable=False)
    aggregate_id: Mapped[str] = mapped_column(String(255), nullable=False)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


Index("idx_processing_job_status_updated_at", ProcessingJob.status, ProcessingJob.updated_at)
Index("idx_processing_job_folder_id", ProcessingJob.folder_id)
Index("idx_processing_step_job_id_status", ProcessingStep.job_id, ProcessingStep.status)
Index("idx_folder_state_status_updated_at", FolderState.status, FolderState.updated_at)
Index("idx_validation_result_folder_id", ValidationResult.folder_id)
Index("idx_processing_error_job_id", ProcessingError.job_id)
Index("idx_processing_error_folder_id", ProcessingError.folder_id)
Index("idx_outbox_event_created_at", OutboxEvent.created_at)
