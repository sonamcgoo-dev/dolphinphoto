"""
DolphinPhoto AI Studio - Dream Video API
AI-powered video generation endpoints
"""
from __future__ import annotations

import base64
import io

from fastapi import APIRouter, HTTPException
from PIL import Image
from pydantic import BaseModel, Field

from app.services.video_service import video_service

router = APIRouter(prefix="/dream-video", tags=["dream_video"])


class DreamVideoGenerateRequest(BaseModel):
    image: str = Field(..., description="Base64 encoded starting image")
    prompt: str = Field("", description="Dream description/prompt")
    duration: float = Field(5.0, ge=1.0, le=60.0)
    fps: int = Field(24, ge=15, le=60)
    motion_strength: float = Field(0.5, ge=0.0, le=1.0)
    seed: int | None = None
    style: str = Field("natural", description="Style preset: natural, ethereal, dramatic, psychedelic")


class GlowupRequest(BaseModel):
    image: str = Field(..., description="Base64 encoded image")
    intensity: float = Field(0.7, ge=0.0, le=1.0)
    enhance_face: bool = Field(True)
    brighten: bool = Field(True)
    smooth_skin: bool = Field(True)
    sharpen: bool = Field(True)


def decode_image(base64_str: str) -> Image.Image:
    """Decode base64 string to PIL Image."""
    if base64_str.startswith("data:"):
        base64_str = base64_str.split(",")[1]
    img_bytes = base64.b64decode(base64_str)
    return Image.open(io.BytesIO(img_bytes))


@router.post("/generate", response_model=dict)
async def generate_dream_video(request: DreamVideoGenerateRequest) -> dict:
    """Generate AI-powered dream video from image."""
    try:
        image = decode_image(request.image)
        
        result = await video_service.generate_dream_video(
            image=image,
            prompt=request.prompt,
            duration=request.duration,
            fps=request.fps,
            motion_strength=request.motion_strength,
            seed=request.seed,
            style=request.style,
        )
        
        return {
            "success": True,
            "video": result,
            "params": {
                "prompt": request.prompt,
                "duration": request.duration,
                "fps": request.fps,
                "motion_strength": request.motion_strength,
                "style": request.style,
            },
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/glowup", response_model=dict)
async def apply_glowup(request: GlowupRequest) -> dict:
    """Apply AI glowup enhancement to photo."""
    try:
        from app.services.filter_service import filter_service
        from app.core.config import get_settings
        import uuid
        
        settings = get_settings()
        
        image = decode_image(request.image)
        
        # Apply glowup steps
        # 1. Face enhancement if enabled
        if request.enhance_face:
            try:
                from app.services.ai_service import ai_service
                image_data = await ai_service.face_restore(image, strength=request.intensity)
                # Load the processed image
                from pathlib import Path
                if Path(image_data.get("path", "")).exists():
                    image = Image.open(image_data["path"])
            except Exception:
                pass  # Continue without face enhancement
        
        # 2. Smooth skin filter
        if request.smooth_skin:
            image = await filter_service.apply_filter(
                image, "smooth_skin", request.intensity
            )
        
        # 3. Brighten
        if request.brighten:
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(1.0 + 0.2 * request.intensity)
        
        # 4. Sharpen
        if request.sharpen:
            from PIL import ImageFilter
            image = image.filter(ImageFilter.SHARPEN)
        
        # 5. Apply a subtle glow filter
        image = await filter_service.apply_filter(image, "glow", 0.3 * request.intensity)
        
        # Save result
        img_id = str(uuid.uuid4())
        output_path = settings.OUTPUTS_DIR / f"{img_id}_glowup.png"
        image.save(output_path, "PNG")
        
        return {
            "success": True,
            "image": {
                "id": f"{img_id}_glowup",
                "path": str(output_path),
            },
            "applied": {
                "face_enhancement": request.enhance_face,
                "skin_smoothing": request.smooth_skin,
                "brightening": request.brighten,
                "sharpening": request.sharpen,
                "glow": True,
            },
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/styles", response_model=dict)
async def get_styles() -> dict:
    """Get available dream video styles."""
    return {
        "success": True,
        "styles": [
            {"id": "natural", "name": "Natural", "description": "Gentle, realistic motion"},
            {"id": "ethereal", "name": "Ethereal", "description": "Dreamy, soft glow effects"},
            {"id": "dramatic", "name": "Dramatic", "description": "Bold colors and movement"},
            {"id": "psychedelic", "name": "Psychedelic", "description": "Intense color shifts and waves"},
            {"id": "cinematic", "name": "Cinematic", "description": "Film-like atmosphere"},
            {"id": "vaporwave", "name": "Vaporwave", "description": "Retro-futuristic aesthetic"},
        ],
    }
