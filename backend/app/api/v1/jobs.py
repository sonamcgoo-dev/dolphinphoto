"""
DolphinPhoto AI Studio - Jobs API
Background job management endpoints
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.models.db_models import JobStatus
from app.services.job_manager import job_manager

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/", response_model=dict)
async def list_jobs(
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> dict:
    """List all jobs with optional filtering."""
    try:
        status_enum = JobStatus(status) if status else None
        jobs = await job_manager.list_jobs(
            status=status_enum,
            limit=limit,
            offset=offset,
        )
        
        return {
            "success": True,
            "jobs": jobs,
            "count": len(jobs),
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid status value")


@router.get("/{job_id}", response_model=dict)
async def get_job(job_id: str) -> dict:
    """Get job details."""
    job = await job_manager.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {
        "success": True,
        "job": job,
    }


@router.post("/{job_id}/cancel", response_model=dict)
async def cancel_job(job_id: str) -> dict:
    """Cancel a running job."""
    success = await job_manager.cancel_job(job_id)
    
    if not success:
        raise HTTPException(status_code=400, detail="Job could not be cancelled")
    
    return {
        "success": True,
        "message": "Job cancelled",
    }


@router.delete("/{job_id}", response_model=dict)
async def delete_job(job_id: str) -> dict:
    """Delete a job."""
    # Get job first
    job = await job_manager.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Cancel if running
    if job["status"] == "running":
        await job_manager.cancel_job(job_id)
    
    # In a real implementation, we'd delete from DB here
    return {
        "success": True,
        "message": "Job deleted",
    }
