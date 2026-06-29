"""
DolphinPhoto AI Studio - AI Service
Stable Diffusion and AI image generation/processing
"""
from __future__ import annotations

import asyncio
import base64
import io
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import torch
except ImportError:
    torch = None

from PIL import Image

try:
    from diffusers import (
        StableDiffusionImg2ImgPipeline,
        StableDiffusionInpaintPipeline,
        StableDiffusionPipeline,
        DPMSolverMultistepScheduler,
        EulerDiscreteScheduler,
    )
    from diffusers.pipelines import pipeline_loading_info
except ImportError:
    StableDiffusionPipeline = None
    StableDiffusionImg2ImgPipeline = None
    StableDiffusionInpaintPipeline = None

try:
    from huggingface_hub import hf_hub_download, model_info
except ImportError:
    hf_hub_download = None
    model_info = None

try:
    from safetensors.torch import load_file as load_safetensors
except ImportError:
    load_safetensors = None

from app.core.config import get_settings
from app.services.device_service import device_service

settings = get_settings()


class AIService:
    """Service for AI-powered image generation and processing."""
    
    def __init__(self):
        self._txt2img_pipeline = None
        self._img2img_pipeline = None
        self._inpaint_pipeline = None
        self._loaded_models: dict[str, Any] = {}
        self._device = device_service.info.device
        self._lock = asyncio.Lock()
        self._torch_available = torch is not None
        self._initialized = False
    
    def _ensure_initialized(self):
        """Lazy initialization - ensure all handlers are bound."""
        if not self._initialized:
            self._initialized = True
    
    @property
    def device(self) -> str:
        """Get current device."""
        return self._device
    
    @property
    def is_available(self) -> bool:
        """Check if AI services are available."""
        return self._torch_available
    
    async def load_model(
        self,
        model_name: str = "stabilityai/stable-diffusion-2-1",
        model_type: str = "checkpoint",
    ) -> dict:
        """Load an AI model into memory."""
        async with self._lock:
            cache_key = f"{model_type}:{model_name}"
            
            if cache_key in self._loaded_models:
                return {"status": "already_loaded", "model": model_name}
            
            try:
                if model_type == "checkpoint":
                    pipeline = StableDiffusionPipeline.from_pretrained(
                        model_name,
                        torch_dtype=torch.float16 if self._device != "cpu" else torch.float32,
                        safety_checker=None if not settings.SAFETY_CHECKER else None,
                        use_safetensors=True,
                    )
                    pipeline = pipeline.to(self._device)
                    
                    if settings.USE_XFORMERS:
                        try:
                            pipeline.enable_xformers_memory_efficient_attention()
                        except Exception:
                            pass
                    
                    if settings.ATTENTION_SLICE:
                        pipeline.enable_attention_slicing()
                    
                    if settings.VAE_SLICE:
                        pipeline.enable_vae_slicing()
                    
                    self._loaded_models[cache_key] = pipeline
                    
                elif model_type == "lora":
                    # LoRA loading handled separately
                    pass
                
                return {"status": "loaded", "model": model_name}
                
            except Exception as e:
                return {"status": "error", "error": str(e)}
    
    async def unload_model(self, model_name: str, model_type: str = "checkpoint") -> dict:
        """Unload a model from memory."""
        cache_key = f"{model_type}:{model_name}"
        
        if cache_key in self._loaded_models:
            del self._loaded_models[cache_key]
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        
        return {"status": "unloaded"}
    
    async def txt2img(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: int = 512,
        height: int = 512,
        steps: int = 30,
        cfg_scale: float = 7.5,
        seed: int | None = None,
        batch_size: int = 1,
        model_name: str | None = None,
        lora_paths: list[str] | None = None,
        progress_callback: Any = None,
    ) -> list[dict]:
        """Generate images from text prompts."""
        model_key = f"checkpoint:{model_name or settings.DEFAULT_MODEL}"
        
        if model_key not in self._loaded_models:
            await self.load_model(model_name or settings.DEFAULT_MODEL)
        
        pipeline = self._loaded_models.get(model_key)
        if not pipeline:
            raise RuntimeError("No model loaded")
        
        generator = None
        if seed is not None:
            generator = torch.Generator(device=self._device).manual_seed(seed)
        
        def progress_handler(step, timestep, latents):
            if progress_callback:
                progress_callback(step / steps)
        
        scheduler_config = pipeline.scheduler.config
        pipeline.scheduler = DPMSolverMultistepScheduler.from_config(scheduler_config)
        
        with torch.inference_mode():
            result = pipeline(
                prompt=prompt,
                negative_prompt=negative_prompt,
                width=width,
                height=height,
                num_inference_steps=steps,
                guidance_scale=cfg_scale,
                generator=generator,
                num_images_per_prompt=batch_size,
                callback=progress_handler if progress_callback else None,
            )
        
        images = []
        for idx, img in enumerate(result.images):
            img_id = str(uuid.uuid4())
            output_path = settings.OUTPUTS_DIR / f"{img_id}.png"
            img.save(output_path, "PNG")
            
            images.append({
                "id": img_id,
                "path": str(output_path),
                "seed": int(generator.initial_seed()[0]) + idx if generator else None,
            })
        
        return images
    
    async def img2img(
        self,
        image: Image.Image,
        prompt: str,
        negative_prompt: str = "",
        strength: float = 0.75,
        steps: int = 30,
        cfg_scale: float = 7.5,
        seed: int | None = None,
        model_name: str | None = None,
    ) -> dict:
        """Transform an image using AI."""
        model_key = f"checkpoint:{model_name or settings.DEFAULT_MODEL}"
        
        if model_key not in self._loaded_models:
            await self.load_model(model_name or settings.DEFAULT_MODEL)
        
        pipeline = self._loaded_models.get(model_key)
        if not pipeline:
            raise RuntimeError("No model loaded")
        
        generator = None
        if seed is not None:
            generator = torch.Generator(device=self._device).manual_seed(seed)
        
        w, h = image.size
        img = image.resize((512, 512), resample=Image.Resampling.LANCZOS)
        
        with torch.inference_mode():
            result = pipeline(
                prompt=prompt,
                image=img,
                negative_prompt=negative_prompt,
                strength=strength,
                num_inference_steps=steps,
                guidance_scale=cfg_scale,
                generator=generator,
            )
        
        output_img = result.images[0].resize((w, h), resample=Image.Resampling.LANCZOS)
        img_id = str(uuid.uuid4())
        output_path = settings.OUTPUTS_DIR / f"{img_id}.png"
        output_img.save(output_path, "PNG")
        
        return {
            "id": img_id,
            "path": str(output_path),
            "seed": int(generator.initial_seed()[0]) if generator else None,
        }
    
    async def inpaint(
        self,
        image: Image.Image,
        mask: Image.Image,
        prompt: str,
        negative_prompt: str = "",
        steps: int = 30,
        cfg_scale: float = 7.5,
        seed: int | None = None,
    ) -> dict:
        """Inpaint regions of an image."""
        model_key = f"checkpoint:{settings.DEFAULT_MODEL}"
        
        if model_key not in self._loaded_models:
            await self.load_model(settings.DEFAULT_MODEL)
        
        pipeline = self._loaded_models.get(model_key)
        if not pipeline:
            raise RuntimeError("No model loaded")
        
        generator = None
        if seed is not None:
            generator = torch.Generator(device=self._device).manual_seed(seed)
        
        w, h = image.size
        img = image.resize((512, 512), resample=Image.Resampling.LANCZOS)
        msk = mask.resize((512, 512), resample=Image.Resampling.LANCZOS)
        
        with torch.inference_mode():
            result = pipeline(
                prompt=prompt,
                image=img,
                mask_image=msk,
                negative_prompt=negative_prompt,
                num_inference_steps=steps,
                guidance_scale=cfg_scale,
                generator=generator,
            )
        
        output_img = result.images[0].resize((w, h), resample=Image.Resampling.LANCZOS)
        img_id = str(uuid.uuid4())
        output_path = settings.OUTPUTS_DIR / f"{img_id}.png"
        output_img.save(output_path, "PNG")
        
        return {
            "id": img_id,
            "path": str(output_path),
        }
    
    async def upscale(
        self,
        image: Image.Image,
        scale: int = 2,
        model: str = "RealESRGAN-x2plus",
    ) -> dict:
        """Upscale an image using AI."""
        try:
            from basicsr.archs.rrdbnet_arch import RRDBNet
            from realesrgan import RealESRGANer
            
            if self._device == "cuda":
                model_path = settings.MODELS_DIR / f"{model}.pth"
                if not model_path.exists():
                    model_path = "weights/RealESRGAN-x2plus.pth"
                
                nets = RRDBNet(num_intch=32, num_feat=64, num_block=23, num_gch_g=32, num_gch_a=32)
                upsampler = RealESRGANer(
                    scale=scale,
                    model_path=str(model_path),
                    model=nets,
                    tile=0,
                    tile_pad=10,
                    pre_pad=0,
                    half=True if self._device == "cuda" else False,
                    device=self._device,
                )
            else:
                upsampler = None
                image = image.resize(
                    (image.width * scale, image.height * scale),
                    resample=Image.Resampling.LANCZOS
                )
        except Exception:
            image = image.resize(
                (image.width * scale, image.height * scale),
                resample=Image.Resampling.LANCZOS
            )
        
        img_id = str(uuid.uuid4())
        output_path = settings.OUTPUTS_DIR / f"{img_id}.png"
        image.save(output_path, "PNG")
        
        return {
            "id": img_id,
            "path": str(output_path),
        }
    
    async def remove_background(self, image: Image.Image) -> dict:
        """Remove background from image."""
        try:
            from rembg import remove
            
            output = remove(image, alpha_matting=True, alpha_matting_foreground_threshold=240)
            
            img_id = str(uuid.uuid4())
            output_path = settings.OUTPUTS_DIR / f"{img_id}.png"
            output.save(output_path, "PNG")
            
            return {
                "id": img_id,
                "path": str(output_path),
            }
        except Exception as e:
            raise RuntimeError(f"Background removal failed: {e}")
    
    async def face_restore(self, image: Image.Image, strength: float = 1.0) -> dict:
        """Restore and enhance faces in image."""
        try:
            from gfpgan import GFPGANer
            
            restorer = GFPGANer(
                model_path="experiments pretrained_models GFPGANv1.3.pth",
                upscale=1,
                arch="clean",
                channel_multiplier=2,
                bg_tile=400,
                device=self._device,
            )
            
            _, restored_img = restorer.enhance(
                image,
                has_aligned=False,
                only_center_face=False,
                paste_back=True,
                weight=strength,
            )
            
            img_id = str(uuid.uuid4())
            output_path = settings.OUTPUTS_DIR / f"{img_id}.png"
            restored_img.save(output_path, "PNG")
            
            return {
                "id": img_id,
                "path": str(output_path),
            }
        except Exception as e:
            # Fallback to just returning original
            img_id = str(uuid.uuid4())
            output_path = settings.OUTPUTS_DIR / f"{img_id}.png"
            image.save(output_path, "PNG")
            return {
                "id": img_id,
                "path": str(output_path),
                "warning": f"Face restore unavailable: {e}",
            }


# Global instance
ai_service = AIService()
