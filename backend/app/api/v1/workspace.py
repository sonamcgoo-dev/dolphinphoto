"""
DolphinPhoto AI Studio - Workspace API
File management and workspace browsing endpoints
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel, Field

from app.core.config import get_settings

router = APIRouter(prefix="/workspace", tags=["workspace"])
settings = get_settings()


class FileInfo(BaseModel):
    name: str
    path: str
    is_dir: bool
    size: int
    modified: float
    extension: Optional[str] = None


@router.get("/browse", response_model=dict)
async def browse_workspace(
    path: str = "",
    show_hidden: bool = False,
) -> dict:
    """Browse workspace directory."""
    if path:
        browse_path = Path(settings.WORKSPACE_DIR) / path
    else:
        browse_path = settings.WORKSPACE_DIR
    
    if not browse_path.exists():
        browse_path = settings.WORKSPACE_DIR
    
    if not str(browse_path).startswith(str(settings.WORKSPACE_DIR)):
        raise HTTPException(status_code=403, detail="Access denied: path outside workspace")
    
    items = []
    
    try:
        for item in sorted(browse_path.iterdir()):
            if item.name.startswith('.') and not show_hidden:
                continue
            
            items.append(FileInfo(
                name=item.name,
                path=str(item.relative_to(settings.WORKSPACE_DIR)),
                is_dir=item.is_dir(),
                size=item.stat().st_size if item.is_file() else 0,
                modified=item.stat().st_mtime,
                extension=item.suffix.lstrip('.') if item.is_file() else None,
            ))
    except PermissionError:
        raise HTTPException(status_code=403, detail="Permission denied")
    
    return {
        "success": True,
        "path": str(browse_path.relative_to(settings.WORKSPACE_DIR)),
        "items": [item.model_dump() for item in items],
        "count": len(items),
    }


@router.get("/outputs", response_model=dict)
async def list_outputs(
    limit: int = 50,
    offset: int = 0,
) -> dict:
    """List generated output files."""
    outputs_dir = settings.OUTPUTS_DIR
    
    if not outputs_dir.exists():
        return {
            "success": True,
            "files": [],
            "count": 0,
        }
    
    files = sorted(
        outputs_dir.glob("*"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )[offset:offset+limit]
    
    items = []
    for f in files:
        items.append({
            "name": f.name,
            "path": str(f.relative_to(settings.WORKSPACE_DIR)),
            "type": "image" if f.suffix.lower() in ['.png', '.jpg', '.jpeg', '.webp', '.gif'] else "video" if f.suffix.lower() in ['.mp4', '.webm', '.mov'] else "file",
            "size": f.stat().st_size,
            "modified": f.stat().st_mtime,
        })
    
    return {
        "success": True,
        "files": items,
        "count": len(items),
    }


@router.post("/upload", response_model=dict)
async def upload_to_workspace(
    file: UploadFile = File(...),
    subdir: str = "",
) -> dict:
    """Upload file to workspace."""
    if subdir:
        target_dir = settings.WORKSPACE_DIR / subdir
    else:
        target_dir = settings.TEMP_DIR
    
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Sanitize filename
    filename = file.filename or "upload"
    safe_name = "".join(c for c in filename if c.isalnum() or c in "._-")
    target_path = target_dir / safe_name
    
    try:
        contents = await file.read()
        with open(target_path, "wb") as f:
            f.write(contents)
        
        return {
            "success": True,
            "file": {
                "name": safe_name,
                "path": str(target_path.relative_to(settings.WORKSPACE_DIR)),
                "size": len(contents),
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/file", response_model=dict)
async def delete_file(path: str) -> dict:
    """Delete a file from workspace."""
    file_path = settings.WORKSPACE_DIR / path
    
    if not str(file_path).startswith(str(settings.WORKSPACE_DIR)):
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        if file_path.is_file():
            file_path.unlink()
        else:
            import shutil
            shutil.rmtree(file_path)
        
        return {
            "success": True,
            "message": f"Deleted: {path}",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/info", response_model=dict)
async def get_workspace_info() -> dict:
    """Get workspace information and disk usage."""
    import shutil
    
    def get_dir_size(path: Path) -> int:
        total = 0
        try:
            for item in path.rglob('*'):
                if item.is_file():
                    total += item.stat().st_size
        except PermissionError:
            pass
        return total
    
    total_size = get_dir_size(settings.WORKSPACE_DIR)
    
    # Get sizes of subdirectories
    subdirs = {}
    for subdir in ["models", "outputs", "temp", "workflows", "projects", "cache"]:
        subdir_path = settings.WORKSPACE_DIR / subdir
        if subdir_path.exists():
            subdirs[subdir] = get_dir_size(subdir_path)
    
    return {
        "success": True,
        "workspace": {
            "path": str(settings.WORKSPACE_DIR),
            "total_size": total_size,
            "total_size_formatted": shutil.disk_usage(settings.WORKSPACE_DIR).total,
            "subdirectories": subdirs,
        },
        "limits": {
            "max_file_size": 100 * 1024 * 1024,  # 100MB
            "supported_formats": ["png", "jpg", "jpeg", "webp", "gif", "mp4", "webm", "mov"],
        },
    }
