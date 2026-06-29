"""Services package"""
from app.services.ai_service import AIService
from app.services.filter_service import FilterService
from app.services.video_service import VideoService

ai_service = AIService()
filter_service = FilterService()
video_service = VideoService()

__all__ = ["ai_service", "filter_service", "video_service", "AIService", "FilterService", "VideoService"]
