"""
DolphinPhoto AI Studio - Video API
Video processing, generation, and editing endpoints
"""
from __future__ import annotations

import base64
import io
from typing import Any

from fastapi import APIRouter, HTTPException, UploadFile
from PIL import Image
from pydantic import BaseModel, Field

from app.services.video_service import video_service

router = APIRouter(prefix="/video", tags=["video"])


class VideoGenerateRequest(BaseModel):
    images: list[str] = Field(..., description="Base64 encoded images")
    duration: float = Field(3.0, ge=1.0, le=30.0, description="Duration per image")
    transition: str = Field("fade", description="Transition type")
    transition_duration: float = Field(1.0, ge=0.0, le=5.0)
    output_fps: int = Field(30, ge=15, le=60)
    resolution: tuple[int, int] | None = None


class DreamVideoRequest(BaseModel):
    image: str = Field(..., description="Base64 encoded image")
    prompt: str = Field("", description="Dream description")
    duration: float = Field(5.0, ge=1.0, le=60.0)
    fps: int = Field(24, ge=15, le=60)
    motion_strength: float = Field(0.5, ge=0.0, le=1.0)
    seed: int | None = None


class VideoEnhanceRequest(BaseModel):
    video_path: str = Field(..., description="Path to video file")
    upscale: float = Field(1.0, ge=1.0, le=4.0)
    denoise: bool = True
    stabilize: bool = False


class VideoTrimRequest(BaseModel):
    video_path: str = Field(..., description="Path to video file")
    start_time: float = Field(..., ge=0.0)
    end_time: float = Field(..., gt=0)


class VideoSpeedRequest(BaseModel):
    video_path: str = Field(..., description="Path to video file")
    speed_factor: float = Field(..., ge=0.25, le=4.0)


def decode_image(base64_str: str) -> Image.Image:
    """Decode base64 string to PIL Image."""
    if base64_str.startswith("data:"):
        base64_str = base64_str.split(",")[1]
    img_bytes = base64.b64decode(base64_str)
    return Image.open(io.BytesIO(img_bytes))


@router.post("/generate", response_model=dict)
async def generate_video(request: VideoGenerateRequest) -> dict:
    """Generate slideshow video from images."""
    try:
        images = [decode_image(img) for img in request.images]
        
        result = await video_service.create_slideshow(
            images=images,
            duration=request.duration,
            transition=request.transition,
            transition_duration=request.transition_duration,
            output_fps=request.output_fps,
        )
        
        return {
            "success": True,
            "video": result,
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dream", response_model=dict)
async def create_dream_video(request: DreamVideoRequest) -> dict:
    """Generate AI-powered dream video."""
    try:
        image = decode_image(request.image)
        
        result = await video_service.generate_dream_video(
            image=image,
            prompt=request.prompt,
            duration=request.duration,
            fps=request.fps,
            motion_strength=request.motion_strength,
            seed=request.seed,
        )
        
        return {
            "success": True,
            "video": result,
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/enhance", response_model=dict)
async def enhance_video(request: VideoEnhanceRequest) -> dict:
    """Enhance video quality."""
    try:
        result = await video_service.enhance_video(
            input_path=request.video_path,
            upscale=request.upscale,
            denoise=request.denoise,
            stabilize=request.stabilize,
        )
        
        return {
            "success": True,
            "video": result,
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trim", response_model=dict)
async def trim_video(request: VideoTrimRequest) -> dict:
    """Trim video to specified time range."""
    try:
        result = await video_service.trim_video(
            input_path=request.video_path,
            start_time=request.start_time,
            end_time=request.end_time,
        )
        
        return {
            "success": True,
            "video": result,
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/speed", response_model=dict)
async def change_video_speed(request: VideoSpeedRequest) -> dict:
    """Change video playback speed."""
    try:
        result = await video_service.change_speed(
            input_path=request.video_path,
            speed_factor=request.speed_factor,
        )
        
        return {
            "success": True,
            "video": result,
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reverse", response_model=dict)
async def reverse_video(video_path: str) -> dict:
    """Reverse video playback."""
    try:
        result = await video_service.reverse_video(video_path=video_path)
        
        return {
            "success": True,
            "video": result,
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload", response_model=dict)
async def upload_video(file: UploadFile) -> dict:
    """Upload a video file."""
    from app.core.config import get_settings
    import uuid
    
    settings = get_settings()
    
    contents = await file.read()
    
    video_id = str(uuid.uuid4())
    output_path = settings.TEMP_DIR / f"{video_id}_{file.filename}"
    
    with open(output_path, "wb") as f:
        f.write(contents)
    
    info = await video_service.get_video_info(str(output_path))
    
    return {
        "success": True,
        "video": {
            "id": video_id,
            "path": str(output_path),
            "name": file.filename,
            **info,
        },
    }


@router.get("/info/{video_path:path}", response_model=dict)
async def get_video_info(video_path: str) -> dict:
    """Get video metadata."""
    try:
        info = await video_service.get_video_info(video_path)
        return {
            "success": True,
            "info": info,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/transitions", response_model=dict)
async def get_transitions() -> dict:
    """Get available video transitions."""
    return {
        "transitions": [
            {"id": k, "name": v}
            for k, v in video_service.TRANSITION_NAMES.items()
        ]
    }
