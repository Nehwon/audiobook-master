#!/usr/bin/env python3

from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship

from .db import Base

class ProcessingJobStatus(Enum):
    QUEUED = "queued"
    RUNNING = "running"
    RETRY_PENDING = "retry_pending"
    FAILED = "failed"
    DONE = "done"
    CANCELLED = "cancelled"

class ProcessingJob(Base):
    __tablename__ = "processing_job"
    
    id = Column(Integer, primary_key=True)
    status = Column(SQLEnum(ProcessingJobStatus), default=ProcessingJobStatus.QUEUED)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_heartbeat = Column(DateTime, default=datetime.utcnow)
    retry_count = Column(Integer, default=0)
    error_text = Column(Text, nullable=True)

    # Relations
    steps = relationship("ProcessingStep", back_populates="job")
    
    def __repr__(self):
        return f"<ProcessingJob {self.id} status={self.status} retries={self.retry_count}>"

class ProcessingStep(Base):
    __tablename__ = "processing_step"
    
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey("processing_job.id"))
    name = Column(String(100))
    status = Column(SQLEnum(ProcessingJobStatus), default=ProcessingJobStatus.QUEUED)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Relations
    job = relationship("ProcessingJob", back_populates="steps")

    def __repr__(self):
        return f"<ProcessingStep {self.id} name={self.name} status={self.status}>"

class FolderState(Base):
    __tablename__ = "folder_state"
    
    id = Column(Integer, primary_key=True)
    path = Column(String(500), unique=True)
    status = Column(String(50))
    last_processed = Column(DateTime, nullable=True)
    error_count = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<FolderState {self.path} status={self.status}>"

class ValidationResult(Base):
    __tablename__ = "validation_result"
    
    id = Column(Integer, primary_key=True)
    folder_id = Column(Integer, ForeignKey("folder_state.id"))
    validator_name = Column(String(100))
    is_valid = Column(Boolean)
    validation_time = Column(DateTime, default=datetime.utcnow)
    details = Column(Text, nullable=True)
    
    # Relations
    folder = relationship("FolderState", backref="validations")

    def __repr__(self):
        return f"<ValidationResult {self.id} valid={self.is_valid}>"

class ProcessingError(Base):
    __tablename__ = "processing_error"
    
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey("processing_job.id"), nullable=True)
    folder_id = Column(Integer, ForeignKey("folder_state.id"), nullable=True)
    error_code = Column(String(50))
    message = Column(Text)
    stack_trace = Column(Text, nullable=True)
    occurred_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    job = relationship("ProcessingJob", backref="errors")
    folder = relationship("FolderState", backref="errors")

    def __repr__(self):
        return f"<ProcessingError {self.error_code} at {self.occurred_at}>"

class OutboxEvent(Base):
    __tablename__ = "outbox_event"
    
    id = Column(Integer, primary_key=True)
    event_type = Column(String(100))
    payload = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<OutboxEvent {self.event_type} at {self.created_at}>"
