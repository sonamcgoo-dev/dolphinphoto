"""
DolphinPhoto AI Studio - Video Service
Video processing, generation, and editing capabilities
"""
from __future__ import annotations

import asyncio
import io
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from PIL import Image

try:
    import imageio.v3 as iio
except ImportError:
    iio = None

from app.core.config import get_settings
from app.services.device_service import device_service

settings = get_settings()


class VideoService:
    """Service for video processing and generation."""
    
    TRANSITIONS = [
        "fade", "dissolve", "slide_left", "slide_right", "slide_up", "slide_down",
        "zoom_in", "zoom_out", "wipe", "blur", "pixelate", "glitch", "none"
    ]
    
    TRANSITION_NAMES = {
        "fade": "🎬 Fade",
        "dissolve": "💫 Dissolve",
        "slide_left": "➡️ Slide Left",
        "slide_right": "⬅️ Slide Right",
        "slide_up": "⬆️ Slide Up",
        "slide_down": "⬇️ Slide Down",
        "zoom_in": "🔍 Zoom In",
        "zoom_out": "🔍 Zoom Out",
        "wipe": "🧹 Wipe",
        "blur": "🌫️ Blur",
        "pixelate": "👾 Pixelate",
        "glitch": "💠 Glitch",
        "none": "⚡ None (Cut)",
    }
    
    @property
    def device(self) -> str:
        """Get current device."""
        return device_service.info.device
    
    async def create_slideshow(
        self,
        images: list[Image.Image],
        duration: float = 3.0,
        transition: str = "fade",
        transition_duration: float = 1.0,
        transition_frames: int = 30,
        output_fps: int = 30,
        resolution: tuple[int, int] | None = None,
        music_path: str | None = None,
    ) -> dict:
        """Create a slideshow video from images."""
        if not images:
            raise ValueError("No images provided")
        
        output_id = str(uuid.uuid4())
        output_path = settings.OUTPUTS_DIR / f"{output_id}.mp4"
        
        # Resize images to consistent resolution
        if resolution is None:
            resolution = images[0].size
            # Ensure even dimensions for video encoding
            resolution = (resolution[0] // 2 * 2, resolution[1] // 2 * 2)
        
        processed_images = []
        for img in images:
            # Resize maintaining aspect ratio
            img_ratio = img.width / img.height
            target_ratio = resolution[0] / resolution[1]
            
            if img_ratio > target_ratio:
                new_width = resolution[0]
                new_height = int(resolution[0] / img_ratio)
            else:
                new_height = resolution[1]
                new_width = int(resolution[1] * img_ratio)
            
            new_width = new_width // 2 * 2
            new_height = new_height // 2 * 2
            
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Center on black background
            canvas = Image.new("RGB", resolution, (0, 0, 0))
            paste_x = (resolution[0] - new_width) // 2
            paste_y = (resolution[1] - new_height) // 2
            canvas.paste(img, (paste_x, paste_y))
            
            processed_images.append(canvas)
        
        # Generate transition frames
        def blend_frames(img1: Image.Image, img2: Image.Image, alpha: float) -> Image.Image:
            """Blend two frames with alpha."""
            return Image.blend(img1, img2, alpha)
        
        video_frames = []
        transition_images = []
        
        for i in range(len(processed_images)):
            # Add frames for this image
            frame_count = int(duration * output_fps)
            
            if i < len(processed_images) - 1:
                frame_count -= transition_frames
                
                # Generate transition frames
                for j in range(transition_frames):
                    alpha = j / transition_frames
                    
                    if transition == "fade":
                        frame = blend_frames(processed_images[i], processed_images[i+1], alpha)
                    elif transition == "dissolve":
                        frame = blend_frames(processed_images[i], processed_images[i+1], alpha)
                    elif transition == "slide_left":
                        img1_arr = np.array(processed_images[i])
                        img2_arr = np.array(processed_images[i+1])
                        shift = int(resolution[0] * alpha)
                        frame_arr = np.zeros_like(img1_arr)
                        frame_arr[:, :resolution[0]-shift] = img1_arr[:, shift:]
                        frame_arr[:, resolution[0]-shift:] = img2_arr[:, :shift]
                        frame = Image.fromarray(frame_arr)
                    elif transition == "slide_right":
                        img1_arr = np.array(processed_images[i])
                        img2_arr = np.array(processed_images[i+1])
                        shift = int(resolution[0] * alpha)
                        frame_arr = np.zeros_like(img1_arr)
                        frame_arr[:, shift:] = img1_arr[:, :resolution[0]-shift]
                        frame_arr[:, :shift] = img2_arr[:, resolution[0]-shift:]
                        frame = Image.fromarray(frame_arr)
                    elif transition == "zoom_in":
                        scale = 1 + alpha * 0.2
                        center_x, center_y = resolution[0] // 2, resolution[1] // 2
                        zoomed = processed_images[i].resize(
                            (int(resolution[0] * scale), int(resolution[1] * scale)),
                            Image.Resampling.LANCZOS
                        )
                        frame_arr = np.array(zoomed)
                        start_x = (frame_arr.shape[1] - resolution[0]) // 2
                        start_y = (frame_arr.shape[0] - resolution[1]) // 2
                        frame = Image.fromarray(frame_arr[start_y:start_y+resolution[1], start_x:start_x+resolution[0]])
                        frame = Image.blend(frame, processed_images[i+1], alpha)
                    elif transition == "zoom_out":
                        frame = Image.blend(processed_images[i+1], processed_images[i], alpha)
                    elif transition == "wipe":
                        wipe_pos = int(resolution[0] * alpha)
                        frame_arr = np.array(processed_images[i]).copy()
                        frame_arr[:, wipe_pos:] = np.array(processed_images[i+1])[:, :resolution[0]-wipe_pos]
                        frame = Image.fromarray(frame_arr)
                    elif transition == "blur":
                        blur_radius = int(20 * (1 - abs(0.5 - alpha) * 2))
                        if blur_radius > 0:
                            img1_blur = processed_images[i].filter(ImageFilter.GaussianBlur(blur_radius))
                            img2_blur = processed_images[i+1].filter(ImageFilter.GaussianBlur(blur_radius))
                        else:
                            img1_blur = processed_images[i]
                            img2_blur = processed_images[i+1]
                        frame = blend_frames(img1_blur, img2_blur, alpha)
                    elif transition == "pixelate":
                        pixel_size = int(50 * (1 - abs(0.5 - alpha) * 2))
                        if pixel_size > 1:
                            small_size = (max(1, resolution[0] // pixel_size), max(1, resolution[1] // pixel_size))
                            img1_pixel = processed_images[i].resize(small_size, Image.Resampling.NEAREST).resize(resolution, Image.Resampling.NEAREST)
                            img2_pixel = processed_images[i+1].resize(small_size, Image.Resampling.NEAREST).resize(resolution, Image.Resampling.NEAREST)
                        else:
                            img1_pixel = processed_images[i]
                            img2_pixel = processed_images[i+1]
                        frame = blend_frames(img1_pixel, img2_pixel, alpha)
                    elif transition == "glitch":
                        frame = blend_frames(processed_images[i], processed_images[i+1], alpha)
                        # Add glitch effect
                        frame_arr = np.array(frame)
                        if alpha > 0.3 and alpha < 0.7:
                            shift = np.random.randint(-20, 20)
                            frame_arr[:, :, 0] = np.roll(frame_arr[:, :, 0], shift, axis=1)
                            frame_arr[:, :, 2] = np.roll(frame_arr[:, :, 2], -shift, axis=1)
                        frame = Image.fromarray(frame_arr)
                    else:
                        frame = processed_images[i]
                    
                    transition_images.append(frame)
            
            # Add main image frames
            for _ in range(frame_count):
                video_frames.append(processed_images[i])
        
        # Add transition frames at the end
        video_frames.extend(transition_images)
        
        # Write video
        await self._write_video(output_path, video_frames, output_fps)
        
        return {
            "id": output_id,
            "path": str(output_path),
            "duration": len(video_frames) / output_fps,
            "frames": len(video_frames),
            "resolution": resolution,
            "fps": output_fps,
            "transition": transition,
        }
    
    async def generate_dream_video(
        self,
        image: Image.Image,
        prompt: str = "",
        duration: float = 5.0,
        fps: int = 24,
        motion_strength: float = 0.5,
        seed: int | None = None,
        style: str = "natural",
        progress_callback: Any = None,
    ) -> dict:
        """Generate AI-powered dream video from image."""
        output_id = str(uuid.uuid4())
        output_path = settings.OUTPUTS_DIR / f"{output_id}.mp4"
        
        resolution = (image.width // 2 * 2, image.height // 2 * 2)
        image = image.resize(resolution, Image.Resampling.LANCZOS)
        
        total_frames = int(duration * fps)
        frames = []
        
        # Simple motion simulation - in production would use actual AI model
        for i in range(total_frames):
            progress = i / total_frames
            
            # Create motion effect
            frame = image.copy()
            
            # Add subtle zoom/pulse effect
            scale = 1 + 0.05 * motion_strength * np.sin(progress * np.pi * 4)
            
            if scale != 1:
                new_size = (int(resolution[0] * scale), int(resolution[1] * scale))
                scaled = image.resize(new_size, Image.Resampling.LANCZOS)
                
                # Center crop
                left = (scaled.width - resolution[0]) // 2
                top = (scaled.height - resolution[1]) // 2
                frame = scaled.crop((left, top, left + resolution[0], top + resolution[1]))
            
            # Add gentle color shift
            frame_arr = np.array(frame).astype(np.float32)
            color_shift = 10 * motion_strength * np.sin(progress * np.pi * 6)
            frame_arr[:, :, 0] = np.clip(frame_arr[:, :, 0] + color_shift, 0, 255)  # R
            frame_arr[:, :, 2] = np.clip(frame_arr[:, :, 2] - color_shift, 0, 255)  # B
            frame = Image.fromarray(frame_arr.astype(np.uint8))
            
            frames.append(frame)
            
            if progress_callback:
                progress_callback(i / total_frames)
            
            # Yield control periodically
            if i % 10 == 0:
                await asyncio.sleep(0)
        
        await self._write_video(output_path, frames, fps)
        
        return {
            "id": output_id,
            "path": str(output_path),
            "duration": duration,
            "frames": total_frames,
            "resolution": resolution,
            "fps": fps,
            "prompt": prompt,
        }
    
    async def enhance_video(
        self,
        input_path: str,
        output_path: str | None = None,
        upscale: float = 1.0,
        denoise: bool = True,
        stabilize: bool = False,
        enhance_faces: bool = False,
    ) -> dict:
        """Enhance video quality."""
        if output_path is None:
            output_id = str(uuid.uuid4())
            output_path = settings.OUTPUTS_DIR / f"{output_id}_enhanced.mp4"
        
        cap = cv2.VideoCapture(input_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Calculate new resolution
        new_width = int(width * upscale)
        new_height = int(height * upscale)
        new_width = new_width // 2 * 2
        new_height = new_height // 2 * 2
        
        # Setup output writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(str(output_path), fourcc, fps, (new_width, new_height))
        
        frame_idx = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Apply enhancements
            processed = frame
            
            # Denoise
            if denoise:
                processed = cv2.fastNlMeansDenoisingColored(processed, None, 10, 10, 7, 21)
            
            # Upscale
            if upscale > 1:
                processed = cv2.resize(processed, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
            elif upscale < 1:
                processed = cv2.resize(processed, (new_width, new_height), interpolation=cv2.INTER_AREA)
            
            writer.write(processed)
            frame_idx += 1
        
        cap.release()
        writer.release()
        
        return {
            "id": str(uuid.uuid4()),
            "path": str(output_path),
            "original_frames": total_frames,
            "resolution": (new_width, new_height),
            "fps": fps,
        }
    
    async def apply_filter_to_video(
        self,
        input_path: str,
        filter_name: str,
        intensity: float = 1.0,
        output_path: str | None = None,
    ) -> dict:
        """Apply a filter to entire video."""
        from app.services.filter_service import filter_service
        
        if output_path is None:
            output_id = str(uuid.uuid4())
            output_path = settings.OUTPUTS_DIR / f"{output_id}_filtered.mp4"
        
        cap = cv2.VideoCapture(input_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
        
        frame_idx = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Convert to PIL for filter
            pil_frame = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            
            # Apply filter
            filtered = await filter_service.apply_filter(pil_frame, filter_name, intensity)
            
            # Convert back to OpenCV
            filtered_cv = cv2.cvtColor(np.array(filtered), cv2.COLOR_RGB2BGR)
            writer.write(filtered_cv)
            frame_idx += 1
        
        cap.release()
        writer.release()
        
        return {
            "id": str(uuid.uuid4()),
            "path": str(output_path),
            "frames_processed": frame_idx,
            "filter": filter_name,
            "intensity": intensity,
        }
    
    async def trim_video(
        self,
        input_path: str,
        start_time: float,
        end_time: float,
        output_path: str | None = None,
    ) -> dict:
        """Trim video to specified time range."""
        if output_path is None:
            output_id = str(uuid.uuid4())
            output_path = settings.OUTPUTS_DIR / f"{output_id}_trimmed.mp4"
        
        cap = cv2.VideoCapture(input_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
        
        start_frame = int(start_time * fps)
        end_frame = int(end_time * fps)
        
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        
        for frame_idx in range(start_frame, end_frame):
            ret, frame = cap.read()
            if not ret:
                break
            writer.write(frame)
        
        cap.release()
        writer.release()
        
        return {
            "id": str(uuid.uuid4()),
            "path": str(output_path),
            "start_time": start_time,
            "end_time": end_time,
            "duration": end_time - start_time,
        }
    
    async def change_speed(
        self,
        input_path: str,
        speed_factor: float,
        output_path: str | None = None,
    ) -> dict:
        """Change video playback speed."""
        if output_path is None:
            output_id = str(uuid.uuid4())
            output_path = settings.OUTPUTS_DIR / f"{output_id}_speed.mp4"
        
        cap = cv2.VideoCapture(input_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Output with adjusted frame rate
        output_fps = fps * speed_factor
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(str(output_path), fourcc, output_fps, (width, height))
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Repeat frames for slower, skip for faster
            if speed_factor > 1:
                repeat = int(speed_factor)
                for _ in range(repeat):
                    writer.write(frame)
            else:
                writer.write(frame)
        
        cap.release()
        writer.release()
        
        return {
            "id": str(uuid.uuid4()),
            "path": str(output_path),
            "speed_factor": speed_factor,
        }
    
    async def reverse_video(
        self,
        input_path: str,
        output_path: str | None = None,
    ) -> dict:
        """Reverse video playback."""
        if output_path is None:
            output_id = str(uuid.uuid4())
            output_path = settings.OUTPUTS_DIR / f"{output_id}_reversed.mp4"
        
        cap = cv2.VideoCapture(input_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
        
        frames = []
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(frame)
        
        # Write frames in reverse
        for frame in reversed(frames):
            writer.write(frame)
        
        cap.release()
        writer.release()
        
        return {
            "id": str(uuid.uuid4()),
            "path": str(output_path),
            "reversed": True,
        }
    
    async def get_video_info(self, video_path: str) -> dict:
        """Get video metadata."""
        cap = cv2.VideoCapture(video_path)
        
        info = {
            "path": video_path,
            "fps": cap.get(cv2.CAP_PROP_FPS),
            "frame_count": int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            "duration": cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS) if cap.get(cv2.CAP_PROP_FPS) > 0 else 0,
            "codec": "unknown",
            "size_bytes": Path(video_path).stat().st_size if Path(video_path).exists() else 0,
        }
        
        cap.release()
        return info
    
    async def extract_frames(
        self,
        video_path: str,
        output_dir: str | None = None,
        every_n_frames: int = 1,
        max_frames: int | None = None,
    ) -> dict:
        """Extract frames from video as images."""
        if output_dir is None:
            output_dir = settings.TEMP_DIR / f"frames_{uuid.uuid4().hex[:8]}"
            output_dir.mkdir(parents=True, exist_ok=True)
        else:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
        
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        frame_paths = []
        frame_idx = 0
        saved_idx = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_idx % every_n_frames == 0:
                # Save frame
                frame_path = output_dir / f"frame_{saved_idx:06d}.png"
                cv2.imwrite(str(frame_path), frame)
                frame_paths.append(str(frame_path))
                saved_idx += 1
                
                if max_frames and saved_idx >= max_frames:
                    break
            
            frame_idx += 1
        
        cap.release()
        
        return {
            "output_dir": str(output_dir),
            "frames": frame_paths,
            "total_saved": len(frame_paths),
            "every_n_frames": every_n_frames,
        }
    
    async def _write_video(
        self,
        output_path: Path,
        frames: list[Image.Image],
        fps: int,
    ) -> None:
        """Write frames to video file."""
        if not frames:
            raise ValueError("No frames to write")
        
        first = frames[0]
        width, height = first.size
        width = width // 2 * 2
        height = height // 2 * 2
        
        # Write using OpenCV
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
        
        for frame in frames:
            if frame.size != (width, height):
                frame = frame.resize((width, height), Image.Resampling.LANCZOS)
            
            frame_cv = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)
            writer.write(frame_cv)
        
        writer.release()
    
    async def add_subtitles(
        self,
        video_path: str,
        subtitles: list[dict],
        font_scale: float = 1.0,
        font_thickness: int = 2,
        output_path: str | None = None,
    ) -> dict:
        """Add subtitles to video."""
        if output_path is None:
            output_id = str(uuid.uuid4())
            output_path = settings.OUTPUTS_DIR / f"{output_id}_subtitled.mp4"
        
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
        
        frame_idx = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            current_time = frame_idx / fps
            
            # Find active subtitle
            for sub in subtitles:
                if sub["start"] <= current_time < sub["end"]:
                    text = sub["text"]
                    position = sub.get("position", "bottom")
                    
                    # Calculate text size
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    text_size = cv2.getTextSize(text, font, font_scale, font_thickness)[0]
                    
                    # Position
                    if position == "bottom":
                        x = (width - text_size[0]) // 2
                        y = height - 50
                    elif position == "top":
                        x = (width - text_size[0]) // 2
                        y = 50
                    else:
                        x = (width - text_size[0]) // 2
                        y = height // 2
                    
                    # Draw background
                    cv2.rectangle(
                        frame,
                        (x - 10, y - text_size[1] - 10),
                        (x + text_size[0] + 10, y + 10),
                        (0, 0, 0),
                        -1
                    )
                    
                    # Draw text
                    cv2.putText(
                        frame,
                        text,
                        (x, y),
                        font,
                        font_scale,
                        (255, 255, 255),
                        font_thickness,
                        cv2.LINE_AA
                    )
                    break
            
            writer.write(frame)
            frame_idx += 1
        
        cap.release()
        writer.release()
        
        return {
            "id": str(uuid.uuid4()),
            "path": str(output_path),
            "subtitles_count": len(subtitles),
        }


# Global instance
video_service = VideoService()
