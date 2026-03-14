"""Job model for audio processing tasks."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Integer, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class JobStatus(str, Enum):
    """Job status enumeration."""
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRY_PENDING = "retry_pending"


class Job(Base):
    """Audio processing job model."""
    
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # File paths
    source_path: Mapped[str] = mapped_column(String(500), nullable=False)
    output_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Status and progress
    status: Mapped[JobStatus] = mapped_column(
        String(20), 
        default=JobStatus.QUEUED, 
        nullable=False,
        index=True
    )
    progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Timing
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        nullable=True
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        nullable=True
    )
    
    # Error handling
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_retries: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    
    # Metadata
    metadata: Mapped[Optional[dict]] = mapped_column(
        String(1000), 
        nullable=True,
        default="{}"
    )
    
    # User information
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        String(36), 
        nullable=True,
        index=True
    )
    
    # Processing options
    options: Mapped[Optional[dict]] = mapped_column(
        String(1000), 
        nullable=True,
        default="{}"
    )
    
    def to_dict(self) -> dict:
        """Convert job to dictionary with additional fields."""
        data = super().to_dict()
        data.update({
            "duration": self.calculate_duration(),
            "is_retryable": self.status == JobStatus.FAILED and self.retry_count < self.max_retries,
            "time_elapsed": self.calculate_time_elapsed(),
        })
        return data
    
    def calculate_duration(self) -> Optional[float]:
        """Calculate job duration in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
    
    def calculate_time_elapsed(self) -> Optional[float]:
        """Calculate time elapsed since start."""
        if self.started_at:
            end_time = self.completed_at or datetime.utcnow()
            return (end_time - self.started_at).total_seconds()
        return None
    
    def can_retry(self) -> bool:
        """Check if job can be retried."""
        return (
            self.status == JobStatus.FAILED and 
            self.retry_count < self.max_retries
        )
    
    def increment_retry(self) -> None:
        """Increment retry count."""
        self.retry_count += 1
        self.status = JobStatus.RETRY_PENDING
    
    def start(self) -> None:
        """Mark job as started."""
        self.status = JobStatus.RUNNING
        self.started_at = datetime.utcnow()
    
    def complete(self) -> None:
        """Mark job as completed."""
        self.status = JobStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.progress = 100
    
    def fail(self, error_message: str) -> None:
        """Mark job as failed."""
        self.status = JobStatus.FAILED
        self.completed_at = datetime.utcnow()
        self.error_message = error_message
    
    def cancel(self) -> None:
        """Mark job as cancelled."""
        self.status = JobStatus.CANCELLED
        self.completed_at = datetime.utcnow()
    
    def __repr__(self) -> str:
        return f"<Job(id={self.id}, title={self.title}, status={self.status})>"
