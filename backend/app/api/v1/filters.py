"""
DolphinPhoto AI Studio - Filters API
Filter management and preview endpoints
"""
from __future__ import annotations

import base64
import io

from fastapi import APIRouter, HTTPException
from PIL import Image
from pydantic import BaseModel, Field

from app.services.filter_service import FilterService, FilterCategory

router = APIRouter(prefix="/filters", tags=["filters"])
filter_service = FilterService()


class FilterPreviewRequest(BaseModel):
    image: str = Field(..., description="Base64 encoded image")
    filter_ids: list[str] = Field(..., description="Filter IDs to preview")
    intensity: float = Field(1.0, ge=0.0, le=2.0)


class FilterApplyRequest(BaseModel):
    image: str = Field(..., description="Base64 encoded image")
    filter_id: str = Field(..., description="Filter ID to apply")
    intensity: float = Field(1.0, ge=0.0, le=2.0)
    save: bool = Field(True, description="Save to outputs")


@router.get("/", response_model=dict)
async def get_all_filters() -> dict:
    """Get all available filters organized by category."""
    categories = {}
    
    for cat in FilterCategory:
        filters = filter_service.get_filters_by_category(cat)
        if filters:
            categories[cat.value] = filters
    
    return {
        "success": True,
        "categories": categories,
        "total": len(filter_service.get_all_filters()),
    }


@router.get("/categories", response_model=dict)
async def get_filter_categories() -> dict:
    """Get all filter categories with counts."""
    categories = []
    
    for cat in FilterCategory:
        count = len(filter_service.get_filters_by_category(cat))
        if count > 0:
            categories.append({
                "id": cat.value,
                "name": cat.value.replace("_", " ").title(),
                "count": count,
            })
    
    return {
        "success": True,
        "categories": categories,
    }


@router.get("/{filter_id}", response_model=dict)
async def get_filter_info(filter_id: str) -> dict:
    """Get detailed filter information."""
    filter_info = filter_service.get_filter_info(filter_id)
    
    if not filter_info:
        raise HTTPException(status_code=404, detail="Filter not found")
    
    return {
        "success": True,
        "filter": filter_info,
    }


@router.post("/preview", response_model=dict)
async def preview_filters(request: FilterPreviewRequest) -> dict:
    """Generate previews of multiple filters on an image."""
    try:
        # Decode image
        if request.image.startswith("data:"):
            request.image = request.image.split(",")[1]
        
        img_bytes = base64.b64decode(request.image)
        original = Image.open(io.BytesIO(img_bytes))
        
        previews = []
        
        for filter_id in request.filter_ids:
            try:
                filtered = await filter_service.apply_filter(
                    original, filter_id, request.intensity
                )
                
                # Encode preview
                buffer = io.BytesIO()
                filtered.save(buffer, format="JPEG", quality=85)
                preview_b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
                
                previews.append({
                    "filter_id": filter_id,
                    "preview": f"data:image/jpeg;base64,{preview_b64}",
                    "success": True,
                })
            except Exception as e:
                previews.append({
                    "filter_id": filter_id,
                    "error": str(e),
                    "success": False,
                })
        
        return {
            "success": True,
            "previews": previews,
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/apply", response_model=dict)
async def apply_filter(request: FilterApplyRequest) -> dict:
    """Apply a filter to an image."""
    try:
        # Decode image
        if request.image.startswith("data:"):
            request.image = request.image.split(",")[1]
        
        img_bytes = base64.b64decode(request.image)
        original = Image.open(io.BytesIO(img_bytes))
        
        result = await filter_service.save_filtered_image(
            original, request.filter_id, request.intensity
        )
        
        return {
            "success": True,
            "result": result,
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
