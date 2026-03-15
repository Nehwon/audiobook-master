"""Job schemas for API serialization."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.job import JobStatus


class JobBase(BaseModel):
    """Base job schema."""
    title: str = Field(..., min_length=1, max_length=255, description="Job title")
    description: Optional[str] = Field(None, description="Job description")
    source_path: str = Field(..., description="Source file path")
    output_path: Optional[str] = Field(None, description="Output file path")
    metadata: Optional[dict] = Field(default={}, description="Job metadata")
    options: Optional[dict] = Field(default={}, description="Processing options")


class JobCreate(JobBase):
    """Schema for creating a job."""
    user_id: Optional[str] = Field(None, description="User ID")
    max_retries: int = Field(default=3, ge=0, le=10, description="Maximum retry attempts")


class JobUpdate(BaseModel):
    """Schema for updating a job."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[JobStatus] = None
    progress: Optional[int] = Field(None, ge=0, le=100)
    error_message: Optional[str] = None
    metadata: Optional[dict] = None
    options: Optional[dict] = None


class JobResponse(JobBase):
    """Schema for job response."""
    id: str = Field(..., description="Job ID")
    status: JobStatus = Field(..., description="Job status")
    progress: int = Field(..., description="Progress percentage")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    started_at: Optional[datetime] = Field(None, description="Start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    error_message: Optional[str] = Field(None, description="Error message")
    retry_count: int = Field(..., description="Current retry count")
    max_retries: int = Field(..., description="Maximum retry attempts")
    user_id: Optional[str] = Field(None, description="User ID")
    
    # Computed fields
    duration: Optional[float] = Field(None, description="Job duration in seconds")
    is_retryable: bool = Field(..., description="Whether job can be retried")
    time_elapsed: Optional[float] = Field(None, description="Time elapsed since start")
    
    class Config:
        from_attributes = True


class JobListResponse(BaseModel):
    """Schema for job list response."""
    jobs: list[JobResponse] = Field(..., description="List of jobs")
    total: int = Field(..., description="Total number of jobs")
    page: int = Field(default=1, description="Current page")
    per_page: int = Field(default=20, description="Items per page")


class JobStatsResponse(BaseModel):
    """Schema for job statistics response."""
    total: int = Field(..., description="Total jobs")
    queued: int = Field(..., description="Queued jobs")
    running: int = Field(..., description="Running jobs")
    completed: int = Field(..., description="Completed jobs")
    failed: int = Field(..., description="Failed jobs")
    cancelled: int = Field(..., description="Cancelled jobs")
    
    # Additional metrics
    avg_duration: Optional[float] = Field(None, description="Average duration in seconds")
    success_rate: float = Field(..., description="Success rate percentage")
    active_jobs: int = Field(..., description="Currently active jobs")
