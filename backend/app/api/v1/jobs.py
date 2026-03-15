"""Jobs API endpoints."""

from __future__ import annotations

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from app.core.database import get_db
from app.models.job import Job, JobStatus
from app.schemas.job import (
    JobCreate, 
    JobResponse, 
    JobUpdate, 
    JobListResponse, 
    JobStatsResponse
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=JobResponse, status_code=201)
async def create_job(
    job_data: JobCreate,
    db: AsyncSession = Depends(get_db)
) -> Job:
    """Create a new job."""
    try:
        job = Job(**job_data.dict())
        db.add(job)
        await db.commit()
        await db.refresh(job)
        
        logger.info(f"Created job {job.id}: {job.title}")
        return job
        
    except Exception as e:
        logger.error(f"Failed to create job: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create job")


@router.get("/", response_model=JobListResponse)
async def list_jobs(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    status: JobStatus | None = Query(None, description="Filter by status"),
    db: AsyncSession = Depends(get_db)
) -> JobListResponse:
    """List jobs with pagination."""
    try:
        # Build query
        query = select(Job)
        
        # Apply status filter
        if status:
            query = query.where(Job.status == status)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination and ordering
        offset = (page - 1) * per_page
        query = query.order_by(desc(Job.created_at)).offset(offset).limit(per_page)
        
        # Execute query
        result = await db.execute(query)
        jobs = result.scalars().all()
        
        # Calculate pages
        pages = (total + per_page - 1) // per_page
        
        return JobListResponse(
            jobs=jobs,
            total=total,
            page=page,
            per_page=per_page,
            pages=pages
        )
        
    except Exception as e:
        logger.error(f"Failed to list jobs: {e}")
        raise HTTPException(status_code=500, detail="Failed to list jobs")


@router.get("/stats", response_model=JobStatsResponse)
async def get_job_stats(db: AsyncSession = Depends(get_db)) -> JobStatsResponse:
    """Get job statistics."""
    try:
        # Get status counts
        status_counts = {}
        for status in JobStatus:
            query = select(func.count(Job.id)).where(Job.status == status)
            result = await db.execute(query)
            status_counts[status.value] = result.scalar() or 0
        
        # Get total jobs
        total_query = select(func.count(Job.id))
        total_result = await db.execute(total_query)
        total = total_result.scalar() or 0
        
        # Calculate success rate
        completed = status_counts.get("completed", 0)
        failed = status_counts.get("failed", 0)
        finished_jobs = completed + failed
        success_rate = (completed / finished_jobs * 100) if finished_jobs > 0 else 0
        
        # Get active jobs (queued + running)
        active_jobs = status_counts.get("queued", 0) + status_counts.get("running", 0)
        
        # Calculate average duration (simplified)
        avg_duration = None  # TODO: Implement proper duration calculation
        
        return JobStatsResponse(
            total=total,
            queued=status_counts.get("queued", 0),
            running=status_counts.get("running", 0),
            completed=completed,
            failed=failed,
            cancelled=status_counts.get("cancelled", 0),
            avg_duration=avg_duration,
            success_rate=round(success_rate, 2),
            active_jobs=active_jobs
        )
        
    except Exception as e:
        logger.error(f"Failed to get job stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get job statistics")


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str,
    db: AsyncSession = Depends(get_db)
) -> Job:
    """Get a specific job."""
    try:
        query = select(Job).where(Job.id == job_id)
        result = await db.execute(query)
        job = result.scalar_one_or_none()
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return job
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get job {job_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get job")


@router.put("/{job_id}", response_model=JobResponse)
async def update_job(
    job_id: str,
    job_update: JobUpdate,
    db: AsyncSession = Depends(get_db)
) -> Job:
    """Update a job."""
    try:
        # Get existing job
        query = select(Job).where(Job.id == job_id)
        result = await db.execute(query)
        job = result.scalar_one_or_none()
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Update fields
        update_data = job_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(job, field, value)
        
        await db.commit()
        await db.refresh(job)
        
        logger.info(f"Updated job {job_id}")
        return job
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update job {job_id}: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update job")


@router.delete("/{job_id}")
async def delete_job(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a job."""
    try:
        # Get existing job
        query = select(Job).where(Job.id == job_id)
        result = await db.execute(query)
        job = result.scalar_one_or_none()
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Check if job can be deleted
        if job.status == JobStatus.RUNNING:
            raise HTTPException(
                status_code=400, 
                detail="Cannot delete a running job"
            )
        
        await db.delete(job)
        await db.commit()
        
        logger.info(f"Deleted job {job_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete job {job_id}: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete job")


@router.post("/{job_id}/retry", response_model=JobResponse)
async def retry_job(
    job_id: str,
    db: AsyncSession = Depends(get_db)
) -> Job:
    """Retry a failed job."""
    try:
        # Get existing job
        query = select(Job).where(Job.id == job_id)
        result = await db.execute(query)
        job = result.scalar_one_or_none()
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Check if job can be retried
        if not job.can_retry():
            raise HTTPException(
                status_code=400,
                detail="Job cannot be retried"
            )
        
        # Increment retry and reset status
        job.increment_retry()
        job.error_message = None
        job.progress = 0
        
        await db.commit()
        await db.refresh(job)
        
        logger.info(f"Retrying job {job_id}")
        return job
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retry job {job_id}: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to retry job")


@router.post("/{job_id}/cancel", response_model=JobResponse)
async def cancel_job(
    job_id: str,
    db: AsyncSession = Depends(get_db)
) -> Job:
    """Cancel a job."""
    try:
        # Get existing job
        query = select(Job).where(Job.id == job_id)
        result = await db.execute(query)
        job = result.scalar_one_or_none()
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Check if job can be cancelled
        if job.status in [JobStatus.COMPLETED, JobStatus.CANCELLED]:
            raise HTTPException(
                status_code=400,
                detail="Job cannot be cancelled"
            )
        
        # Cancel the job
        job.cancel()
        
        await db.commit()
        await db.refresh(job)
        
        logger.info(f"Cancelled job {job_id}")
        return job
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel job {job_id}: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to cancel job")
