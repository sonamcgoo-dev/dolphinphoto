"""
DolphinPhoto AI Studio - Job Manager
Background job processing and tracking
"""
from __future__ import annotations

import asyncio
import json
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Coroutine

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models.db_models import Job, JobStatus, JobType


class JobManager:
    """Manages background processing jobs."""
    
    def __init__(self):
        self._jobs: dict[str, asyncio.Task] = {}
        self._callbacks: dict[str, list[Callable]] = {}
        self._lock = asyncio.Lock()
    
    async def create_job(
        self,
        job_type: JobType,
        params: dict[str, Any],
        db: AsyncSession | None = None,
    ) -> str:
        """Create a new processing job."""
        job_id = str(uuid.uuid4())
        
        if db is None:
            async with AsyncSessionLocal() as db:
                job = Job(
                    id=job_id,
                    type=job_type,
                    status=JobStatus.PENDING,
                    params=params,
                    progress=0.0,
                )
                db.add(job)
                await db.commit()
        else:
            job = Job(
                id=job_id,
                type=job_type,
                status=JobStatus.PENDING,
                params=params,
                progress=0.0,
            )
            db.add(job)
            await db.commit()
        
        return job_id
    
    async def start_job(
        self,
        job_id: str,
        coro: Coroutine,
        callbacks: list[Callable] | None = None,
    ) -> None:
        """Start a job coroutine in the background."""
        async with self._lock:
            if callbacks:
                self._callbacks[job_id] = callbacks
            
            task = asyncio.create_task(self._run_job(job_id, coro))
            self._jobs[job_id] = task
    
    async def _run_job(self, job_id: str, coro: Coroutine) -> Any:
        """Run job with progress tracking."""
        try:
            await self.update_job_status(job_id, JobStatus.RUNNING)
            
            result = await coro
            
            await self.update_job_status(job_id, JobStatus.COMPLETED, result=result)
            await self._trigger_callbacks(job_id, result)
            
            return result
            
        except asyncio.CancelledError:
            await self.update_job_status(job_id, JobStatus.CANCELLED)
            raise
        except Exception as e:
            await self.update_job_status(job_id, JobStatus.FAILED, error=str(e))
            await self._trigger_callbacks(job_id, None, str(e))
            raise
    
    async def update_job_progress(self, job_id: str, progress: float) -> None:
        """Update job progress percentage."""
        async with AsyncSessionLocal() as db:
            await db.execute(
                update(Job)
                .where(Job.id == job_id)
                .values(progress=min(progress, 1.0))
            )
            await db.commit()
    
    async def update_job_status(
        self,
        job_id: str,
        status: JobStatus,
        result: Any | None = None,
        error: str | None = None,
        progress: float | None = None,
    ) -> None:
        """Update job status and optionally set result or error."""
        async with AsyncSessionLocal() as db:
            update_values = {"status": status}
            
            if result is not None:
                update_values["result"] = result if isinstance(result, dict) else {"value": result}
            
            if error is not None:
                update_values["error"] = error
            
            if progress is not None:
                update_values["progress"] = progress
            
            if status in (JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED):
                update_values["completed_at"] = datetime.utcnow()
            
            await db.execute(
                update(Job)
                .where(Job.id == job_id)
                .values(**update_values)
            )
            await db.commit()
    
    async def get_job(self, job_id: str) -> dict | None:
        """Get job details."""
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(Job).where(Job.id == job_id))
            job = result.scalar_one_or_none()
            
            if job:
                return {
                    "id": job.id,
                    "type": job.type.value,
                    "status": job.status.value,
                    "params": job.params,
                    "result": job.result,
                    "error": job.error,
                    "progress": job.progress,
                    "created_at": job.created_at.isoformat() if job.created_at else None,
                    "updated_at": job.updated_at.isoformat() if job.updated_at else None,
                    "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                }
            return None
    
    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a running job."""
        async with self._lock:
            if job_id in self._jobs:
                self._jobs[job_id].cancel()
                await self.update_job_status(job_id, JobStatus.CANCELLED)
                return True
        return False
    
    async def list_jobs(
        self,
        status: JobStatus | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict]:
        """List jobs with optional filtering."""
        async with AsyncSessionLocal() as db:
            query = select(Job)
            
            if status:
                query = query.where(Job.status == status)
            
            query = query.order_by(Job.created_at.desc()).limit(limit).offset(offset)
            
            result = await db.execute(query)
            jobs = result.scalars().all()
            
            return [
                {
                    "id": job.id,
                    "type": job.type.value,
                    "status": job.status.value,
                    "params": job.params,
                    "result": job.result,
                    "error": job.error,
                    "progress": job.progress,
                    "created_at": job.created_at.isoformat() if job.created_at else None,
                    "updated_at": job.updated_at.isoformat() if job.updated_at else None,
                    "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                }
                for job in jobs
            ]
    
    async def reset_stale_jobs(self) -> int:
        """Reset jobs that were left in running state."""
        async with AsyncSessionLocal() as db:
            stale_time = datetime.utcnow() - timedelta(hours=1)
            
            result = await db.execute(
                update(Job)
                .where(
                    Job.status == JobStatus.RUNNING,
                    Job.updated_at < stale_time,
                )
                .values(status=JobStatus.FAILED, error="Job timed out")
            )
            await db.commit()
            
            return result.rowcount
    
    async def cleanup_old_jobs(self, days: int = 7) -> int:
        """Remove jobs older than specified days."""
        async with AsyncSessionLocal() as db:
            cutoff = datetime.utcnow() - timedelta(days=days)
            
            from sqlalchemy import delete
            result = await db.execute(
                delete(Job).where(Job.created_at < cutoff)
            )
            await db.commit()
            
            return result.rowcount
    
    async def _trigger_callbacks(
        self, job_id: str, result: Any | None, error: str | None = None
    ) -> None:
        """Trigger registered callbacks for job completion."""
        if job_id in self._callbacks:
            for callback in self._callbacks[job_id]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(result, error)
                    else:
                        callback(result, error)
                except Exception:
                    pass  # Don't let callback errors break anything
            
            del self._callbacks[job_id]


# Global instance
job_manager = JobManager()
