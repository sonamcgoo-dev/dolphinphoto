"""
DolphinPhoto AI Studio - Images API
Image processing, generation, and manipulation endpoints
"""
from __future__ import annotations

import base64
import io
import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from PIL import Image
from pydantic import BaseModel, Field

from app.core.config import get_settings
from app.models.db_models import JobStatus, JobType
from app.services.ai_service import ai_service
from app.services.filter_service import filter_service
from app.services.job_manager import job_manager

router = APIRouter(prefix="/images", tags=["images"])
settings = get_settings()


# ── Request/Response Models ─────────────────────────────────────────────────

class ImageGenerateRequest(BaseModel):
    prompt: str = Field(..., description="Text prompt for generation")
    negative_prompt: str = Field("", description="Negative prompt")
    width: int = Field(512, ge=256, le=2048, description="Image width")
    height: int = Field(512, ge=256, le=2048, description="Image height")
    steps: int = Field(30, ge=1, le=150, description="Inference steps")
    cfg_scale: float = Field(7.5, ge=1.0, le=30.0, description="CFG scale")
    seed: int | None = Field(None, description="Random seed")
    batch_size: int = Field(1, ge=1, le=4, description="Number of images to generate")
    model_name: str | None = Field(None, description="Model to use")


class ImageTransformRequest(BaseModel):
    image: str = Field(..., description="Base64 encoded image")
    prompt: str = Field(..., description="Transformation prompt")
    negative_prompt: str = Field("", description="Negative prompt")
    strength: float = Field(0.75, ge=0.0, le=1.0, description="Transformation strength")
    steps: int = Field(30, ge=1, le=150, description="Inference steps")
    cfg_scale: float = Field(7.5, ge=1.0, le=30.0, description="CFG scale")
    seed: int | None = Field(None, description="Random seed")


class ImageInpaintRequest(BaseModel):
    image: str = Field(..., description="Base64 encoded image")
    mask: str = Field(..., description="Base64 encoded mask")
    prompt: str = Field(..., description="Inpainting prompt")
    steps: int = Field(30, ge=1, le=150, description="Inference steps")
    cfg_scale: float = Field(7.5, ge=1.0, le=30.0, description="CFG scale")
    seed: int | None = Field(None, description="Random seed")


class ImageUpscaleRequest(BaseModel):
    image: str = Field(..., description="Base64 encoded image")
    scale: int = Field(2, ge=2, le=4, description="Upscale factor")
    model: str = Field("RealESRGAN-x2plus", description="Upscaler model")


class ImageFilterRequest(BaseModel):
    image: str = Field(..., description="Base64 encoded image")
    filter_id: str = Field(..., description="Filter ID to apply")
    intensity: float = Field(1.0, ge=0.0, le=2.0, description="Filter intensity")


class ColorAdjustRequest(BaseModel):
    image: str = Field(..., description="Base64 encoded image")
    brightness: float = Field(1.0, ge=0.0, le=3.0, description="Brightness")
    contrast: float = Field(1.0, ge=0.0, le=3.0, description="Contrast")
    saturation: float = Field(1.0, ge=0.0, le=3.0, description="Saturation")
    hue: float = Field(0, ge=-180, le=180, description="Hue shift in degrees")
    temperature: float = Field(0, ge=-100, le=100, description="Color temperature")
    tint: float = Field(0, ge=-100, le=100, description="Tint adjustment")


class ImageFormatConvertRequest(BaseModel):
    image: str = Field(..., description="Base64 encoded image")
    format: str = Field("PNG", description="Output format: PNG, JPEG, WebP, BMP, TIFF")
    quality: int = Field(95, ge=1, le=100, description="Output quality")


# ── Utility Functions ────────────────────────────────────────────────────────

def decode_image(base64_str: str) -> Image.Image:
    """Decode base64 string to PIL Image."""
    if base64_str.startswith("data:"):
        base64_str = base64_str.split(",")[1]
    
    img_bytes = base64.b64decode(base64_str)
    return Image.open(io.BytesIO(img_bytes))


def encode_image(image: Image.Image, format: str = "PNG") -> str:
    """Encode PIL Image to base64 string."""
    buffer = io.BytesIO()
    if format.upper() == "JPEG":
        image.save(buffer, format="JPEG", quality=95)
    else:
        image.save(buffer, format=format.upper())
    
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


# ── Image Generation Endpoints ───────────────────────────────────────────────

@router.post("/generate", response_model=dict)
async def generate_image(request: ImageGenerateRequest) -> dict:
    """Generate images from text prompt."""
    try:
        result = await ai_service.txt2img(
            prompt=request.prompt,
            negative_prompt=request.negative_prompt,
            width=request.width,
            height=request.height,
            steps=request.steps,
            cfg_scale=request.cfg_scale,
            seed=request.seed,
            batch_size=request.batch_size,
            model_name=request.model_name,
        )
        
        return {
            "success": True,
            "images": result,
            "params": {
                "prompt": request.prompt,
                "width": request.width,
                "height": request.height,
                "steps": request.steps,
            },
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/transform", response_model=dict)
async def transform_image(request: ImageTransformRequest) -> dict:
    """Transform image using AI (img2img)."""
    try:
        image = decode_image(request.image)
        
        result = await ai_service.img2img(
            image=image,
            prompt=request.prompt,
            negative_prompt=request.negative_prompt,
            strength=request.strength,
            steps=request.steps,
            cfg_scale=request.cfg_scale,
            seed=request.seed,
        )
        
        return {
            "success": True,
            "image": result,
            "params": {
                "prompt": request.prompt,
                "strength": request.strength,
                "steps": request.steps,
            },
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/inpaint", response_model=dict)
async def inpaint_image(request: ImageInpaintRequest) -> dict:
    """Inpaint regions of an image."""
    try:
        image = decode_image(request.image)
        mask = decode_image(request.mask)
        
        # Ensure mask is grayscale
        if mask.mode != "L":
            mask = mask.convert("L")
        
        result = await ai_service.inpaint(
            image=image,
            mask=mask,
            prompt=request.prompt,
            steps=request.steps,
            cfg_scale=request.cfg_scale,
            seed=request.seed,
        )
        
        return {
            "success": True,
            "image": result,
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Image Processing Endpoints ───────────────────────────────────────────────

@router.post("/upscale", response_model=dict)
async def upscale_image(request: ImageUpscaleRequest) -> dict:
    """Upscale an image using AI."""
    try:
        image = decode_image(request.image)
        
        result = await ai_service.upscale(
            image=image,
            scale=request.scale,
            model=request.model,
        )
        
        return {
            "success": True,
            "image": result,
            "scale": request.scale,
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/remove-background", response_model=dict)
async def remove_background(request: ImageUpscaleRequest) -> dict:
    """Remove background from image."""
    try:
        image = decode_image(request.image)
        
        result = await ai_service.remove_background(image)
        
        return {
            "success": True,
            "image": result,
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/restore-face", response_model=dict)
async def restore_face(request: ImageUpscaleRequest) -> dict:
    """Restore and enhance faces."""
    try:
        image = decode_image(request.image)
        
        result = await ai_service.face_restore(image)
        
        return {
            "success": True,
            "image": result,
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Filter Endpoints ─────────────────────────────────────────────────────────

@router.get("/filters", response_model=dict)
async def get_filters(category: str | None = None) -> dict:
    """Get all available filters."""
    if category:
        filters = filter_service.get_filters_by_category(category)
    else:
        filters = filter_service.get_all_filters()
    
    return {
        "filters": filters,
        "count": len(filters),
    }


@router.get("/filters/{filter_id}", response_model=dict)
async def get_filter(filter_id: str) -> dict:
    """Get filter information."""
    filter_info = filter_service.get_filter_info(filter_id)
    
    if not filter_info:
        raise HTTPException(status_code=404, detail="Filter not found")
    
    return filter_info


@router.post("/filters/apply", response_model=dict)
async def apply_filter(request: ImageFilterRequest) -> dict:
    """Apply a filter to an image."""
    try:
        image = decode_image(request.image)
        
        result = await filter_service.save_filtered_image(
            image=image,
            filter_id=request.filter_id,
            intensity=request.intensity,
        )
        
        return {
            "success": True,
            "image": result,
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Color Adjustment Endpoints ──────────────────────────────────────────────

@router.post("/color-adjust", response_model=dict)
async def adjust_color(request: ColorAdjustRequest) -> dict:
    """Apply color adjustments to an image."""
    try:
        image = decode_image(request.image)
        
        # Apply brightness
        if request.brightness != 1.0:
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(request.brightness)
        
        # Apply contrast
        if request.contrast != 1.0:
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(request.contrast)
        
        # Apply saturation
        if request.saturation != 1.0:
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(request.saturation)
        
        # Apply hue shift (approximation)
        if request.hue != 0:
            from PIL import ImageEnhance, ImageOps
            # Simple hue shift via HSV
            hsv_image = image.convert("HSV")
            hsv_array = hsv_image.load()
            width, height = image.size
            
            shift = int(request.hue * 2.55) % 256  # Convert to HSV range
            for y in range(height):
                for x in range(width):
                    h, s, v = hsv_array[x, y]
                    h = (h + shift) % 256
                    hsv_array[x, y] = (h, s, v)
            
            image = hsv_image.convert("RGB")
        
        # Apply temperature/tint (approximation)
        if request.temperature != 0 or request.tint != 0:
            import numpy as np
            img_array = np.array(image).astype(np.float32)
            
            # Temperature: warmer (redder) or cooler (bluer)
            temp_shift = request.temperature / 100 * 30
            img_array[:,:,0] = np.clip(img_array[:,:,0] + temp_shift, 0, 255)  # R
            img_array[:,:,2] = np.clip(img_array[:,:,2] - temp_shift, 0, 255)  # B
            
            # Tint: green or magenta
            tint_shift = request.tint / 100 * 30
            img_array[:,:,1] = np.clip(img_array[:,:,1] + tint_shift, 0, 255)  # G
            
            image = Image.fromarray(img_array.astype(np.uint8))
        
        # Save result
        img_id = str(uuid.uuid4())
        output_path = settings.OUTPUTS_DIR / f"{img_id}.png"
        image.save(output_path, "PNG")
        
        return {
            "success": True,
            "image": {
                "id": img_id,
                "path": str(output_path),
            },
            "adjustments": {
                "brightness": request.brightness,
                "contrast": request.contrast,
                "saturation": request.saturation,
                "hue": request.hue,
                "temperature": request.temperature,
                "tint": request.tint,
            },
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Format Conversion Endpoints ──────────────────────────────────────────────

@router.post("/convert", response_model=dict)
async def convert_format(request: ImageFormatConvertRequest) -> dict:
    """Convert image to different format."""
    try:
        image = decode_image(request.image)
        
        format_upper = request.format.upper()
        if format_upper not in ["PNG", "JPEG", "WEBP", "BMP", "TIFF"]:
            raise HTTPException(status_code=400, detail="Unsupported format")
        
        # Handle transparency for JPEG
        if format_upper == "JPEG" and image.mode in ("RGBA", "LA", "P"):
            background = Image.new("RGB", image.size, (255, 255, 255))
            if image.mode == "P":
                image = image.convert("RGBA")
            background.paste(image, mask=image.split()[-1])
            image = background
        
        # Save
        img_id = str(uuid.uuid4())
        ext = format_upper.lower() if format_upper != "TIFF" else "tiff"
        output_path = settings.OUTPUTS_DIR / f"{img_id}.{ext}"
        
        save_kwargs = {}
        if format_upper in ["JPEG", "WEBP"]:
            save_kwargs["quality"] = request.quality
        
        image.save(output_path, format=format_upper, **save_kwargs)
        
        return {
            "success": True,
            "image": {
                "id": img_id,
                "path": str(output_path),
                "format": format_upper,
                "size": output_path.stat().st_size,
            },
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Upload Endpoint ─────────────────────────────────────────────────────────

@router.post("/upload", response_model=dict)
async def upload_image(file: UploadFile = File(...)) -> dict:
    """Upload an image file."""
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # Validate format
        if image.format not in ["PNG", "JPEG", "WEBP", "BMP", "GIF"]:
            raise HTTPException(status_code=400, detail="Unsupported image format")
        
        # Save to temp
        img_id = str(uuid.uuid4())
        output_path = settings.TEMP_DIR / f"{img_id}.png"
        
        if image.mode == "RGBA":
            image.save(output_path, "PNG")
        else:
            image = image.convert("RGB")
            image.save(output_path, "PNG")
        
        return {
            "success": True,
            "image": {
                "id": img_id,
                "path": str(output_path),
                "name": file.filename,
                "width": image.width,
                "height": image.height,
                "format": image.format,
            },
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{image_id}", response_model=dict)
async def get_image(image_id: str) -> dict:
    """Get image details or content."""
    image_path = settings.OUTPUTS_DIR / f"{image_id}.png"
    
    if not image_path.exists():
        image_path = settings.TEMP_DIR / f"{image_id}.png"
    
    if not image_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    
    image = Image.open(image_path)
    
    return {
        "id": image_id,
        "path": str(image_path),
        "width": image.width,
        "height": image.height,
        "size": image_path.stat().st_size,
    }
