"""
DolphinPhoto AI Studio - Setup API
Initial setup and configuration endpoints
"""
from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.config import get_settings
from app.core.database import AsyncSessionLocal
from app.models.db_models import Setting
from sqlalchemy import select

router = APIRouter(prefix="/setup", tags=["setup"])
settings = get_settings()


class WorkspaceSetupRequest(BaseModel):
    workspace_dir: str = Field(..., description="Path for workspace directory")
    civitai_api_key: str | None = Field(None, description="CivitAI API key")
    hf_token: str | None = Field(None, description="HuggingFace token")


class SettingsUpdateRequest(BaseModel):
    key: str
    value: str


@router.get("/status", response_model=dict)
async def get_setup_status() -> dict:
    """Get current setup status."""
    async with AsyncSessionLocal() as db:
        rows = await db.execute(select(Setting))
        cfg = {r.key: r.value for r in rows.scalars().all()}
    
    return {
        "success": True,
        "setup_complete": cfg.get("setup_complete") == "true",
        "workspace_dir": cfg.get("workspace_dir"),
        "has_civitai_key": bool(cfg.get("civitai_api_key")),
        "device": settings.DEVICE,
        "version": settings.VERSION,
    }


@router.post("/workspace", response_model=dict)
async def setup_workspace(request: WorkspaceSetupRequest) -> dict:
    """Setup workspace directory and save configuration."""
    try:
        workspace_path = Path(request.workspace_dir).expanduser().absolute()
        
        # Create workspace directories
        workspace_path.mkdir(parents=True, exist_ok=True)
        
        subdirs = ["models", "outputs", "workflows", "temp", "projects", "cache", "plugins"]
        for subdir in subdirs:
            (workspace_path / subdir).mkdir(parents=True, exist_ok=True)
        
        # Update settings
        settings.update_workspace(workspace_path)
        settings.ensure_dirs()
        settings.SETUP_COMPLETE = True
        
        if request.civitai_api_key:
            settings.CIVITAI_API_KEY = request.civitai_api_key
        
        if request.hf_token:
            settings.HF_TOKEN = request.hf_token
        
        # Save to database
        async with AsyncSessionLocal() as db:
            settings_to_save = [
                Setting(key="workspace_dir", value=str(workspace_path)),
                Setting(key="setup_complete", value="true"),
            ]
            
            if request.civitai_api_key:
                settings_to_save.append(
                    Setting(key="civitai_api_key", value=request.civitai_api_key)
                )
            
            if request.hf_token:
                settings_to_save.append(
                    Setting(key="hf_token", value=request.hf_token)
                )
            
            for s in settings_to_save:
                db.add(s)
            
            await db.commit()
        
        return {
            "success": True,
            "message": "Workspace configured successfully",
            "workspace_dir": str(workspace_path),
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/settings", response_model=dict)
async def update_setting(request: SettingsUpdateRequest) -> dict:
    """Update a configuration setting."""
    async with AsyncSessionLocal() as db:
        # Check if exists
        result = await db.execute(
            select(Setting).where(Setting.key == request.key)
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            existing.value = request.value
        else:
            setting = Setting(key=request.key, value=request.value)
            db.add(setting)
        
        await db.commit()
    
    # Update runtime settings
    if request.key == "workspace_dir":
        settings.update_workspace(Path(request.value))
    elif request.key == "civitai_api_key":
        settings.CIVITAI_API_KEY = request.value
    elif request.key == "hf_token":
        settings.HF_TOKEN = request.value
    
    return {
        "success": True,
        "key": request.key,
        "value": request.value,
    }


@router.post("/complete", response_model=dict)
async def complete_setup() -> dict:
    """Mark setup as complete."""
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Setting).where(Setting.key == "setup_complete")
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            existing.value = "true"
        else:
            setting = Setting(key="setup_complete", value="true")
            db.add(setting)
        
        await db.commit()
    
    settings.SETUP_COMPLETE = True
    
    return {
        "success": True,
        "message": "Setup marked as complete",
    }
