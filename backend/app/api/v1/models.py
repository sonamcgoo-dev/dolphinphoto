"""
DolphinPhoto AI Studio - Models API
AI model management endpoints
"""
from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.config import get_settings
from app.services.ai_service import ai_service

router = APIRouter(prefix="/models", tags=["models"])
settings = get_settings()


class ModelDownloadRequest(BaseModel):
    model_id: str = Field(..., description="Model ID from CivitAI/HuggingFace")
    source: str = Field("civitai", description="Model source: civitai, huggingface, local")
    model_type: str = Field("checkpoint", description="Model type")
    base_model: str | None = Field(None, description="Base model for LoRA")


class ModelLoadRequest(BaseModel):
    model_name: str = Field(..., description="Model name or path")
    model_type: str = Field("checkpoint", description="Model type")


@router.get("/", response_model=dict)
async def list_models() -> dict:
    """List all installed models."""
    models_dir = settings.MODELS_DIR
    
    if not models_dir.exists():
        return {
            "success": True,
            "models": [],
            "count": 0,
        }
    
    models = []
    
    # Checkpoint models
    checkpoint_exts = ("*.safetensors", "*.ckpt", "*.pth")
    checkpoints: list[Path] = []
    for ext in checkpoint_exts:
        checkpoints.extend(models_dir.glob(ext))
    
    for model_path in checkpoints:
        models.append({
            "id": model_path.stem,
            "name": model_path.name,
            "type": "checkpoint",
            "path": str(model_path),
            "size": model_path.stat().st_size,
            "loaded": False,
        })
    
    # LoRA models
    lora_dir = models_dir / "lora"
    if lora_dir.exists():
        for model_path in lora_dir.glob("*.safetensors"):
            models.append({
                "id": model_path.stem,
                "name": model_path.name,
                "type": "lora",
                "path": str(model_path),
                "size": model_path.stat().st_size,
                "loaded": False,
            })
    
    # VAE models
    vae_dir = models_dir / "vae"
    if vae_dir.exists():
        for model_path in vae_dir.glob("*.safetensors"):
            models.append({
                "id": model_path.stem,
                "name": model_path.name,
                "type": "vae",
                "path": str(model_path),
                "size": model_path.stat().st_size,
                "loaded": False,
            })
    
    return {
        "success": True,
        "models": models,
        "count": len(models),
    }


@router.post("/load", response_model=dict)
async def load_model(request: ModelLoadRequest) -> dict:
    """Load a model into memory."""
    try:
        result = await ai_service.load_model(
            model_name=request.model_name,
            model_type=request.model_type,
        )
        
        return {
            "success": True,
            "result": result,
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/unload", response_model=dict)
async def unload_model(request: ModelLoadRequest) -> dict:
    """Unload a model from memory."""
    result = await ai_service.unload_model(
        model_name=request.model_name,
        model_type=request.model_type,
    )
    
    return {
        "success": True,
        "result": result,
    }


@router.get("/loaded", response_model=dict)
async def get_loaded_models() -> dict:
    """Get currently loaded models."""
    # This would track loaded models in ai_service
    return {
        "success": True,
        "loaded": [],
        "count": 0,
    }


@router.get("/defaults", response_model=dict)
async def get_default_models() -> dict:
    """Get recommended default models."""
    return {
        "success": True,
        "defaults": [
            {
                "name": "stabilityai/stable-diffusion-2-1",
                "type": "checkpoint",
                "description": "Stable Diffusion 2.1 - Balanced quality and speed",
                "size_estimate": "5GB",
                "min_vram": "4GB",
            },
            {
                "name": "stabilityai/stable-diffusion-xl-base-1.0",
                "type": "checkpoint",
                "description": "SDXL 1.0 - Higher quality, more VRAM needed",
                "size_estimate": "6.5GB",
                "min_vram": "8GB",
            },
            {
                "name": "runwayml/stable-diffusion-v1-5",
                "type": "checkpoint",
                "description": "SD 1.5 - Fast, widely compatible",
                "size_estimate": "4GB",
                "min_vram": "2GB",
            },
        ],
    }
