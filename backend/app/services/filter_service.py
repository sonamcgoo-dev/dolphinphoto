"""
DolphinPhoto AI Studio - Filter Service
Comprehensive image filters including Snapchat-style and professional filters
"""
from __future__ import annotations

import io
import uuid
from enum import Enum
from typing import Any

import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageDraw
from scipy import ndimage

from app.core.config import get_settings

settings = get_settings()


class FilterCategory(str, Enum):
    """Filter categories."""
    SOCIAL = "social"  # Snapchat-style filters
    ARTISTIC = "artistic"  # Creative effects
    COLOR = "color"  # Color grading
    ENHANCE = "enhance"  # Enhancement filters
    GLITCH = "glitch"  # Digital effects
    VINTAGE = "vintage"  # Retro effects


class FilterService:
    """Service for applying various image filters."""
    
    # Available filters with their parameters
    FILTERS = {
        # ══════════════════════════════════════════════════════════════════════════
        # SOCIAL FILTERS (Snapchat-style)
        # ══════════════════════════════════════════════════════════════════════════
        "puppy_ears": {
            "name": "🐶 Puppy Ears",
            "category": FilterCategory.SOCIAL,
            "description": "Add cute puppy ears to your photos",
            "params": {"intensity": 1.0, "color": "brown"},
        },
        "cat_ears": {
            "name": "🐱 Cat Ears",
            "category": FilterCategory.SOCIAL,
            "description": "Add adorable cat ears",
            "params": {"intensity": 1.0, "color": "orange"},
        },
        "bunny_ears": {
            "name": "🐰 Bunny Ears",
            "category": FilterCategory.SOCIAL,
            "description": "Fluffy bunny ears filter",
            "params": {"intensity": 1.0, "color": "white"},
        },
        "dog_face": {
            "name": "🐕 Dog Face",
            "category": FilterCategory.SOCIAL,
            "description": "Transform into a cute dog",
            "params": {"intensity": 1.0},
        },
        "cat_face": {
            "name": "😺 Cat Face",
            "category": FilterCategory.SOCIAL,
            "description": "Transform into a cat",
            "params": {"intensity": 1.0},
        },
        "rabbit_face": {
            "name": "🐰 Rabbit Face",
            "category": FilterCategory.SOCIAL,
            "description": "Transform into a rabbit",
            "params": {"intensity": 1.0},
        },
        "fox_face": {
            "name": "🦊 Fox Face",
            "category": FilterCategory.SOCIAL,
            "description": "Become a cunning fox",
            "params": {"intensity": 1.0},
        },
        "bear_face": {
            "name": "🐻 Bear Face",
            "category": FilterCategory.SOCIAL,
            "description": "Transform into a bear",
            "params": {"intensity": 1.0},
        },
        "glasses_nerd": {
            "name": "🤓 Nerd Glasses",
            "category": FilterCategory.SOCIAL,
            "description": "Add nerdy glasses",
            "params": {"style": "thick_black", "intensity": 1.0},
        },
        "glasses_sun": {
            "name": "🕶️ Sunglasses",
            "category": FilterCategory.SOCIAL,
            "description": "Cool sunglasses",
            "params": {"style": "aviator", "intensity": 1.0},
        },
        "heart_eyes": {
            "name": "💕 Heart Eyes",
            "category": FilterCategory.SOCIAL,
            "description": "Heart eyes makeup",
            "params": {"intensity": 1.0, "color": "pink"},
        },
        "star_eyes": {
            "name": "⭐ Star Eyes",
            "category": FilterCategory.SOCIAL,
            "description": "Sparkly star eyes",
            "params": {"intensity": 1.0, "color": "gold"},
        },
        "tears_joy": {
            "name": "😂 Tears of Joy",
            "category": FilterCategory.SOCIAL,
            "description": "Crying laughing emoji",
            "params": {"intensity": 1.0},
        },
        "halo": {
            "name": "😇 Angel Halo",
            "category": FilterCategory.SOCIAL,
            "description": "Add an angel halo",
            "params": {"intensity": 1.0, "glow": True},
        },
        "devil_horns": {
            "name": "😈 Devil Horns",
            "category": FilterCategory.SOCIAL,
            "description": "Add devil horns",
            "params": {"intensity": 1.0, "color": "red"},
        },
        "crown": {
            "name": "👑 Royal Crown",
            "category": FilterCategory.SOCIAL,
            "description": "Royal crown filter",
            "params": {"intensity": 1.0, "style": "gold"},
        },
        "flowers_crown": {
            "name": "🌸 Flower Crown",
            "category": FilterCategory.SOCIAL,
            "description": "Add a crown of flowers",
            "params": {"intensity": 1.0, "color": "pink"},
        },
        "blush": {
            "name": "😊 Rosy Cheeks",
            "category": FilterCategory.SOCIAL,
            "description": "Add rosy cheeks",
            "params": {"intensity": 0.5, "color": "pink"},
        },
        "lipstick": {
            "name": "💄 Lipstick",
            "category": FilterCategory.SOCIAL,
            "description": "Apply lipstick",
            "params": {"intensity": 0.5, "color": "red"},
        },
        "eyeshadow": {
            "name": "眼 Eyeshadow",
            "category": FilterCategory.SOCIAL,
            "description": "Add colorful eyeshadow",
            "params": {"intensity": 0.5, "color": "purple"},
        },
        "youth_effect": {
            "name": "👶 Youth Effect",
            "category": FilterCategory.SOCIAL,
            "description": "Look younger",
            "params": {"intensity": 0.5},
        },
        "age_effect": {
            "name": "👴 Age Effect",
            "category": FilterCategory.SOCIAL,
            "description": "Look older",
            "params": {"intensity": 0.5},
        },
        "smooth_skin": {
            "name": "✨ Smooth Skin",
            "category": FilterCategory.SOCIAL,
            "description": "Perfect skin complexion",
            "params": {"intensity": 0.7},
        },
        "blemish_remove": {
            "name": "🧹 Blemish Remove",
            "category": FilterCategory.SOCIAL,
            "description": "Remove skin blemishes",
            "params": {"intensity": 1.0},
        },
        "whitening": {
            "name": "🦷 Teeth Whitening",
            "category": FilterCategory.SOCIAL,
            "description": "Whiten teeth",
            "params": {"intensity": 0.5},
        },
        "eye_whitening": {
            "name": "👁️ Eye Whitening",
            "category": FilterCategory.SOCIAL,
            "description": "Brighten eye whites",
            "params": {"intensity": 0.5},
        },
        
        # ══════════════════════════════════════════════════════════════════════════
        # ARTISTIC FILTERS
        # ══════════════════════════════════════════════════════════════════════════
        "vintage_film": {
            "name": "🎞️ Vintage Film",
            "category": FilterCategory.ARTISTIC,
            "description": "Classic film look",
            "params": {"intensity": 1.0, "grain": 0.3},
        },
        "cinematic": {
            "name": "🎬 Cinematic",
            "category": FilterCategory.ARTISTIC,
            "description": "Movie color grade",
            "params": {"intensity": 1.0, "teal_shadows": True},
        },
        "noir": {
            "name": "🎭 Film Noir",
            "category": FilterCategory.ARTISTIC,
            "description": "High contrast B&W",
            "params": {"intensity": 1.0, "contrast": 1.5},
        },
        "sepia": {
            "name": "📜 Sepia",
            "category": FilterCategory.ARTISTIC,
            "description": "Warm sepia tone",
            "params": {"intensity": 1.0},
        },
        "cross_process": {
            "name": "💥 Cross Process",
            "category": FilterCategory.ARTISTIC,
            "description": "Experimental colors",
            "params": {"intensity": 1.0, "shift": "auto"},
        },
        "pop_art": {
            "name": "🎨 Pop Art",
            "category": FilterCategory.ARTISTIC,
            "description": "Bold pop art style",
            "params": {"intensity": 1.0, "saturation": 2.0},
        },
        "comic": {
            "name": "📚 Comic Book",
            "category": FilterCategory.ARTISTIC,
            "description": "Comic book effect",
            "params": {"intensity": 1.0, "lines": True},
        },
        "watercolor": {
            "name": "🎨 Watercolor",
            "category": FilterCategory.ARTISTIC,
            "description": "Soft watercolor painting",
            "params": {"intensity": 1.0},
        },
        "oil_painting": {
            "name": "🖼️ Oil Painting",
            "category": FilterCategory.ARTISTIC,
            "description": "Classical oil painting",
            "params": {"intensity": 1.0},
        },
        "sketch": {
            "name": "✏️ Pencil Sketch",
            "category": FilterCategory.ARTISTIC,
            "description": "Pencil sketch drawing",
            "params": {"intensity": 1.0, "invert": False},
        },
        "pencil_color": {
            "name": "🖍️ Color Pencil",
            "category": FilterCategory.ARTISTIC,
            "description": "Color pencil drawing",
            "params": {"intensity": 1.0},
        },
        "neon_glow": {
            "name": "🌈 Neon Glow",
            "category": FilterCategory.ARTISTIC,
            "description": "Cyberpunk neon style",
            "params": {"intensity": 1.0, "color": "cyan"},
        },
        "neon_pink": {
            "name": "💖 Neon Pink",
            "category": FilterCategory.ARTISTIC,
            "description": "Pink neon glow",
            "params": {"intensity": 1.0},
        },
        "neon_blue": {
            "name": "💙 Neon Blue",
            "category": FilterCategory.ARTISTIC,
            "description": "Blue neon glow",
            "params": {"intensity": 1.0},
        },
        "neon_purple": {
            "name": "💜 Neon Purple",
            "category": FilterCategory.ARTISTIC,
            "description": "Purple neon glow",
            "params": {"intensity": 1.0},
        },
        "holographic": {
            "name": "✨ Holographic",
            "category": FilterCategory.ARTISTIC,
            "description": "Shimmering holographic",
            "params": {"intensity": 1.0},
        },
        "chrome": {
            "name": "🔘 Chrome",
            "category": FilterCategory.ARTISTIC,
            "description": "Metallic chrome effect",
            "params": {"intensity": 1.0},
        },
        "vaporwave": {
            "name": "🌴 Vaporwave",
            "category": FilterCategory.ARTISTIC,
            "description": "80s vaporwave aesthetic",
            "params": {"intensity": 1.0},
        },
        "synthwave": {
            "name": "🌆 Synthwave",
            "category": FilterCategory.ARTISTIC,
            "description": "Retro synthwave vibes",
            "params": {"intensity": 1.0},
        },
        "dystopic": {
            "name": "🌃 Dystopic",
            "category": FilterCategory.ARTISTIC,
            "description": "Dark dystopian feel",
            "params": {"intensity": 1.0},
        },
        
        # ══════════════════════════════════════════════════════════════════════════
        # COLOR FILTERS
        # ══════════════════════════════════════════════════════════════════════════
        "teal_orange": {
            "name": "🟠💧 Teal & Orange",
            "category": FilterCategory.COLOR,
            "description": "Cinematic teal-orange grade",
            "params": {"intensity": 1.0},
        },
        "golden_hour": {
            "name": "🌅 Golden Hour",
            "category": FilterCategory.COLOR,
            "description": "Warm golden tones",
            "params": {"intensity": 1.0},
        },
        "cool_blue": {
            "name": "❄️ Cool Blue",
            "category": FilterCategory.COLOR,
            "description": "Cool blue tones",
            "params": {"intensity": 1.0},
        },
        "warm_tone": {
            "name": "🔥 Warm Tone",
            "category": FilterCategory.COLOR,
            "description": "Warm color temperature",
            "params": {"intensity": 1.0},
        },
        "cool_tone": {
            "name": "🧊 Cool Tone",
            "category": FilterCategory.COLOR,
            "description": "Cool color temperature",
            "params": {"intensity": 1.0},
        },
        "duotone_blue": {
            "name": "🔵 Duotone Blue",
            "category": FilterCategory.COLOR,
            "description": "Two-tone blue style",
            "params": {"intensity": 1.0, "shadow": "#000066", "highlight": "#66ccff"},
        },
        "duotone_purple": {
            "name": "🟣 Duotone Purple",
            "category": FilterCategory.COLOR,
            "description": "Two-tone purple style",
            "params": {"intensity": 1.0, "shadow": "#330066", "highlight": "#cc66ff"},
        },
        "duotone_sunset": {
            "name": "🌅 Duotone Sunset",
            "category": FilterCategory.COLOR,
            "description": "Sunset duotone style",
            "params": {"intensity": 1.0, "shadow": "#330000", "highlight": "#ffcc66"},
        },
        "color_splash_red": {
            "name": "🔴 Color Splash Red",
            "category": FilterCategory.COLOR,
            "description": "Only red in color",
            "params": {"intensity": 1.0, "color": "red", "grayscale_others": True},
        },
        "color_splash_blue": {
            "name": "🔵 Color Splash Blue",
            "category": FilterCategory.COLOR,
            "description": "Only blue in color",
            "params": {"intensity": 1.0, "color": "blue", "grayscale_others": True},
        },
        "color_splash_green": {
            "name": "🟢 Color Splash Green",
            "category": FilterCategory.COLOR,
            "description": "Only green in color",
            "params": {"intensity": 1.0, "color": "green", "grayscale_others": True},
        },
        "color_pop": {
            "name": "🎨 Color Pop",
            "category": FilterCategory.COLOR,
            "description": "One color pops out",
            "params": {"intensity": 1.0, "target_color": "blue"},
        },
        "saturation_boost": {
            "name": "💥 High Saturation",
            "category": FilterCategory.COLOR,
            "description": "Vibrant colors",
            "params": {"intensity": 1.5},
        },
        "desaturate": {
            "name": "⬜ Desaturate",
            "category": FilterCategory.COLOR,
            "description": "Muted colors",
            "params": {"intensity": 0.3},
        },
        
        # ══════════════════════════════════════════════════════════════════════════
        # ENHANCEMENT FILTERS
        # ══════════════════════════════════════════════════════════════════════════
        "hdr": {
            "name": "📸 HDR Effect",
            "category": FilterCategory.ENHANCE,
            "description": "High dynamic range",
            "params": {"intensity": 1.0},
        },
        "vivid": {
            "name": "🌟 Vivid",
            "category": FilterCategory.ENHANCE,
            "description": "Enhanced vibrancy",
            "params": {"intensity": 1.0},
        },
        "clarity": {
            "name": "🔍 Clarity",
            "category": FilterCategory.ENHANCE,
            "description": "Enhanced midtone contrast",
            "params": {"intensity": 0.5},
        },
        "dramatic": {
            "name": "⚡ Dramatic",
            "category": FilterCategory.ENHANCE,
            "description": "High impact contrast",
            "params": {"intensity": 1.0},
        },
        "fade": {
            "name": "☁️ Fade",
            "category": FilterCategory.ENHANCE,
            "description": "Soft faded look",
            "params": {"intensity": 0.3},
        },
        "high_key": {
            "name": "☀️ High Key",
            "category": FilterCategory.ENHANCE,
            "description": "Bright and airy",
            "params": {"intensity": 1.0},
        },
        "low_key": {
            "name": "🌑 Low Key",
            "category": FilterCategory.ENHANCE,
            "description": "Dark and moody",
            "params": {"intensity": 1.0},
        },
        "sharpen": {
            "name": "🔪 Sharpen",
            "category": FilterCategory.ENHANCE,
            "description": "Enhanced sharpness",
            "params": {"intensity": 1.0},
        },
        "denoise": {
            "name": "🔇 Denoise",
            "category": FilterCategory.ENHANCE,
            "description": "Reduce noise",
            "params": {"intensity": 0.5},
        },
        "dehaze": {
            "name": "🌫️ Dehaze",
            "category": FilterCategory.ENHANCE,
            "description": "Remove fog/haze",
            "params": {"intensity": 1.0},
        },
        "vignette": {
            "name": "⭕ Vignette",
            "category": FilterCategory.ENHANCE,
            "description": "Dark edges",
            "params": {"intensity": 0.5, "size": 0.5},
        },
        "glow": {
            "name": "✨ Soft Glow",
            "category": FilterCategory.ENHANCE,
            "description": "Soft glow effect",
            "params": {"intensity": 0.3, "radius": 10},
        },
        
        # ══════════════════════════════════════════════════════════════════════════
        # GLITCH FILTERS
        # ══════════════════════════════════════════════════════════════════════════
        "glitch": {
            "name": "💠 Glitch",
            "category": FilterCategory.GLITCH,
            "description": "Digital glitch effect",
            "params": {"intensity": 1.0},
        },
        "scanlines": {
            "name": "📺 Scanlines",
            "category": FilterCategory.GLITCH,
            "description": "Retro TV scanlines",
            "params": {"intensity": 0.5, "count": 200},
        },
        "static": {
            "name": "📡 Static Noise",
            "category": FilterCategory.GLITCH,
            "description": "TV static noise",
            "params": {"intensity": 0.3},
        },
        "rgb_shift": {
            "name": "🌈 RGB Shift",
            "category": FilterCategory.GLITCH,
            "description": "RGB color separation",
            "params": {"intensity": 1.0, "amount": 5},
        },
        "chromatic": {
            "name": "🔮 Chromatic",
            "category": FilterCategory.GLITCH,
            "description": "Chromatic aberration",
            "params": {"intensity": 1.0},
        },
        "pixelate": {
            "name": "👾 Pixelate",
            "category": FilterCategory.GLITCH,
            "description": "Retro pixel art",
            "params": {"intensity": 1.0, "block_size": 8},
        },
        "mosaic": {
            "name": "🧩 Mosaic",
            "category": FilterCategory.GLITCH,
            "description": "Mosaic tiles",
            "params": {"intensity": 1.0, "tile_size": 16},
        },
        "corruption": {
            "name": "💀 Corruption",
            "category": FilterCategory.GLITCH,
            "description": "Data corruption effect",
            "params": {"intensity": 0.5},
        },
        "datamosh": {
            "name": "🎞️ Datamosh",
            "category": FilterCategory.GLITCH,
            "description": "Video glitch art",
            "params": {"intensity": 1.0},
        },
        
        # ══════════════════════════════════════════════════════════════════════════
        # VINTAGE FILTERS
        # ══════════════════════════════════════════════════════════════════════════
        "faded_photo": {
            "name": "📷 Faded Photo",
            "category": FilterCategory.VINTAGE,
            "description": "Aged photo look",
            "params": {"intensity": 1.0, "yellow_tint": 0.3},
        },
        "polaroid": {
            "name": "📸 Polaroid",
            "category": FilterCategory.VINTAGE,
            "description": "Instant photo style",
            "params": {"intensity": 1.0, "border": True},
        },
        "kodachrome": {
            "name": "🎞️ Kodachrome",
            "category": FilterCategory.VINTAGE,
            "description": "Classic Kodachrome colors",
            "params": {"intensity": 1.0},
        },
        "ektachrome": {
            "name": "💊 Ektachrome",
            "category": FilterCategory.VINTAGE,
            "description": "Vibrant slide film",
            "params": {"intensity": 1.0},
        },
        "bw_agfa": {
            "name": "⬛ Agfa B&W",
            "category": FilterCategory.VINTAGE,
            "description": "Agfa black & white",
            "params": {"intensity": 1.0, "contrast": 1.2},
        },
        "bw_kodak": {
            "name": "⬛ Kodak B&W",
            "category": FilterCategory.VINTAGE,
            "description": "Kodak black & white",
            "params": {"intensity": 1.0, "warm_tone": True},
        },
        "light_leak": {
            "name": "💡 Light Leak",
            "category": FilterCategory.VINTAGE,
            "description": "Film light leak effect",
            "params": {"intensity": 0.5, "color": "orange"},
        },
        "film_grain": {
            "name": "🌫️ Film Grain",
            "category": FilterCategory.VINTAGE,
            "description": "Classic film grain",
            "params": {"intensity": 0.3, "size": 1.5},
        },
        "dust": {
            "name": "✨ Dust & Scratches",
            "category": FilterCategory.VINTAGE,
            "description": "Aged film imperfections",
            "params": {"intensity": 0.3},
        },
        "halftone": {
            "name": "🖨️ Halftone",
            "category": FilterCategory.VINTAGE,
            "description": "Newspaper print style",
            "params": {"intensity": 1.0, "dot_size": 4},
        },
        "infrared": {
            "name": "🌲 Infrared",
            "category": FilterCategory.VINTAGE,
            "description": "Fake infrared photo",
            "params": {"intensity": 1.0},
        },
        "toy_camera": {
            "name": "📷 Toy Camera",
            "category": FilterCategory.VINTAGE,
            "description": "Lomo camera look",
            "params": {"intensity": 1.0, "vignette": True},
        },
    }
    
    def get_all_filters(self) -> list[dict]:
        """Get all available filters."""
        return [
            {"id": k, **v} for k, v in self.FILTERS.items()
        ]
    
    def get_filters_by_category(self, category: FilterCategory) -> list[dict]:
        """Get filters by category."""
        return [
            {"id": k, **v}
            for k, v in self.FILTERS.items()
            if v["category"] == category
        ]
    
    def get_filter_info(self, filter_id: str) -> dict | None:
        """Get filter information."""
        if filter_id in self.FILTERS:
            return {"id": filter_id, **self.FILTERS[filter_id]}
        return None
    
    async def apply_filter(
        self,
        image: Image.Image,
        filter_id: str,
        intensity: float = 1.0,
        **params,
    ) -> Image.Image:
        """Apply a filter to an image."""
        if filter_id not in self.FILTERS:
            raise ValueError(f"Unknown filter: {filter_id}")
        
        filter_config = self.FILTERS[filter_id]
        category = filter_config["category"]
        
        # Apply base filter based on category
        if category == FilterCategory.SOCIAL:
            result = self._apply_social_filter(image, filter_id, intensity, **params)
        elif category == FilterCategory.ARTISTIC:
            result = self._apply_artistic_filter(image, filter_id, intensity, **params)
        elif category == FilterCategory.COLOR:
            result = self._apply_color_filter(image, filter_id, intensity, **params)
        elif category == FilterCategory.ENHANCE:
            result = self._apply_enhance_filter(image, filter_id, intensity, **params)
        elif category == FilterCategory.GLITCH:
            result = self._apply_glitch_filter(image, filter_id, intensity, **params)
        elif category == FilterCategory.VINTAGE:
            result = self._apply_vintage_filter(image, filter_id, intensity, **params)
        else:
            result = image
        
        return result
    
    def _apply_social_filter(
        self,
        image: Image.Image,
        filter_id: str,
        intensity: float,
        **params,
    ) -> Image.Image:
        """Apply social/Snapchat-style filters."""
        img = image.copy()
        draw = ImageDraw.Draw(img)
        w, h = img.size
        
        if filter_id == "blush":
            # Add rosy cheeks
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(1 + 0.2 * intensity)
            overlay = Image.new("RGBA", img.size, (255, 150, 150, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            
            # Draw blush circles on cheeks
            blush_color = (255, 150, 150, int(128 * intensity))
            overlay_draw.ellipse(
                [int(w * 0.15), int(h * 0.55), int(w * 0.3), int(h * 0.7)],
                fill=blush_color
            )
            overlay_draw.ellipse(
                [int(w * 0.7), int(h * 0.55), int(w * 0.85), int(h * 0.7)],
                fill=blush_color
            )
            
            img = Image.alpha_composite(img.convert("RGBA"), overlay)
            return img.convert("RGB")
        
        elif filter_id == "smooth_skin":
            # Apply skin smoothing
            img_array = np.array(img)
            blurred = cv2.GaussianBlur(img_array, (15, 15), 0)
            mask = np.all(img_array > 30, axis=-1)
            img_array[mask] = blurred[mask]
            return Image.fromarray(img_array)
        
        elif filter_id == "halo":
            # Add angel halo
            img = img.convert("RGBA")
            overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            
            halo_y = int(h * 0.1)
            halo_width = int(w * 0.3)
            halo_height = int(halo_width * 0.15)
            
            glow_color = (255, 215, 0, int(200 * intensity))
            overlay_draw.ellipse(
                [int(w/2 - halo_width/2), halo_y,
                 int(w/2 + halo_width/2), halo_y + halo_height],
                fill=glow_color
            )
            
            return Image.alpha_composite(img, overlay).convert("RGB")
        
        elif filter_id in ["glasses_nerd", "glasses_sun"]:
            # Simple glasses overlay
            img = img.convert("RGBA")
            overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            
            glasses_y = int(h * 0.35)
            glasses_width = int(w * 0.35)
            gap = int(w * 0.08)
            
            if filter_id == "glasses_nerd":
                glass_color = (0, 0, 0, int(180 * intensity))
            else:
                glass_color = (50, 50, 100, int(150 * intensity))
            
            # Left lens
            overlay_draw.ellipse(
                [int(w * 0.2), glasses_y,
                 int(w * 0.2 + glasses_width * 0.4), glasses_y + int(glasses_width * 0.3)],
                outline=glass_color, width=3
            )
            # Right lens
            overlay_draw.ellipse(
                [int(w * 0.6 + gap), glasses_y,
                 int(w * 0.6 + gap + glasses_width * 0.4), glasses_y + int(glasses_width * 0.3)],
                outline=glass_color, width=3
            )
            # Bridge
            overlay_draw.line(
                [int(w * 0.2 + glasses_width * 0.4), glasses_y + int(glasses_width * 0.15),
                 int(w * 0.6 + gap), glasses_y + int(glasses_width * 0.15)],
                fill=glass_color, width=3
            )
            
            return Image.alpha_composite(img, overlay).convert("RGB")
        
        elif filter_id == "crown":
            # Add royal crown
            img = img.convert("RGBA")
            overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            
            crown_y = int(h * 0.05)
            crown_width = int(w * 0.4)
            
            crown_points = [
                (int(w/2 - crown_width/2), crown_y + int(crown_width * 0.3)),
                (int(w/2 - crown_width/2), crown_y),
                (int(w/2 - crown_width/4), crown_y + int(crown_width * 0.15)),
                (int(w/2), crown_y),
                (int(w/2 + crown_width/4), crown_y + int(crown_width * 0.15)),
                (int(w/2 + crown_width/2), crown_y),
                (int(w/2 + crown_width/2), crown_y + int(crown_width * 0.3)),
            ]
            
            crown_color = (255, 215, 0, int(200 * intensity))
            overlay_draw.polygon(crown_points, fill=crown_color, outline=(200, 170, 0, 255))
            
            return Image.alpha_composite(img, overlay).convert("RGB")
        
        return img.convert("RGB")
    
    def _apply_artistic_filter(
        self,
        image: Image.Image,
        filter_id: str,
        intensity: float,
        **params,
    ) -> Image.Image:
        """Apply artistic filters."""
        img = image.copy()
        
        if filter_id == "vintage_film":
            # Apply vintage film look
            img = self._vintage_effect(img, intensity)
        
        elif filter_id == "cinematic":
            # Cinematic color grading
            img = self._cinematic_effect(img, intensity)
        
        elif filter_id == "noir":
            # Film noir B&W
            img = ImageOps.grayscale(img)
            img = ImageEnhance.Contrast(img).enhance(1.5 * intensity)
            img = img.convert("RGB")
        
        elif filter_id == "sepia":
            # Sepia tone
            img = self._sepia_effect(img, intensity)
        
        elif filter_id == "neon_glow":
            img = self._neon_effect(img, intensity, "cyan")
        elif filter_id == "neon_pink":
            img = self._neon_effect(img, intensity, "pink")
        elif filter_id == "neon_blue":
            img = self._neon_effect(img, intensity, "blue")
        elif filter_id == "neon_purple":
            img = self._neon_effect(img, intensity, "purple")
        
        elif filter_id == "sketch":
            img = self._sketch_effect(img, intensity)
        
        elif filter_id == "comic":
            img = self._comic_effect(img, intensity)
        
        elif filter_id == "oil_painting":
            img = img.filter(ImageFilter.SMOOTH_MORE)
            img = img.filter(ImageFilter.EDGE_ENHANCE)
        
        elif filter_id == "watercolor":
            img = img.filter(ImageFilter.SMOOTH)
            img = ImageEnhance.Color(img).enhance(0.8)
            img = ImageEnhance.Contrast(img).enhance(0.9)
        
        elif filter_id == "pop_art":
            img = ImageEnhance.Color(img).enhance(2.0 * intensity)
            img = ImageEnhance.Contrast(img).enhance(1.3)
        
        elif filter_id == "holographic":
            img = self._holographic_effect(img, intensity)
        
        elif filter_id == "chrome":
            img = self._chrome_effect(img, intensity)
        
        elif filter_id == "vaporwave":
            img = self._vaporwave_effect(img, intensity)
        
        elif filter_id == "synthwave":
            img = self._synthwave_effect(img, intensity)
        
        return img
    
    def _apply_color_filter(
        self,
        image: Image.Image,
        filter_id: str,
        intensity: float,
        **params,
    ) -> Image.Image:
        """Apply color grading filters."""
        img = image.copy()
        
        if filter_id == "teal_orange":
            img = self._teal_orange_effect(img, intensity)
        elif filter_id == "golden_hour":
            img = self._golden_hour_effect(img, intensity)
        elif filter_id == "cool_blue":
            img = self._cool_blue_effect(img, intensity)
        elif filter_id == "warm_tone":
            img = ImageEnhance.Color(img).enhance(1 + 0.2 * intensity)
            img = ImageEnhance.Warmth(img).enhance(1.2 * intensity) if hasattr(ImageEnhance, 'Warmth') else img
        elif filter_id == "cool_tone":
            img = ImageEnhance.Color(img).enhance(1 - 0.1 * intensity)
        
        elif filter_id.startswith("duotone_"):
            color = params.get("shadow", "#000000")
            highlight = params.get("highlight", "#FFFFFF")
            img = self._duotone_effect(img, color, highlight, intensity)
        
        elif filter_id.startswith("color_splash_"):
            color = params.get("color", "red")
            img = self._color_splash_effect(img, color, intensity)
        
        elif filter_id == "color_pop":
            img = self._color_pop_effect(img, params.get("target_color", "blue"), intensity)
        
        elif filter_id == "saturation_boost":
            img = ImageEnhance.Color(img).enhance(1 + 0.5 * intensity)
        
        elif filter_id == "desaturate":
            img = ImageEnhance.Color(img).enhance(1 - 0.7 * intensity)
        
        return img
    
    def _apply_enhance_filter(
        self,
        image: Image.Image,
        filter_id: str,
        intensity: float,
        **params,
    ) -> Image.Image:
        """Apply enhancement filters."""
        img = image.copy()
        
        if filter_id == "hdr":
            img = self._hdr_effect(img, intensity)
        elif filter_id == "vivid":
            img = ImageEnhance.Color(img).enhance(1.3)
            img = ImageEnhance.Sharpness(img).enhance(1.2)
        elif filter_id == "clarity":
            img = self._clarity_effect(img, intensity)
        elif filter_id == "dramatic":
            img = ImageEnhance.Contrast(img).enhance(1.5 * intensity)
        elif filter_id == "fade":
            img = ImageEnhance.Contrast(img).enhance(0.9 * intensity)
            img = ImageEnhance.Color(img).enhance(0.85 * intensity)
        elif filter_id == "high_key":
            img = ImageEnhance.Brightness(img).enhance(1.3 * intensity)
            img = ImageEnhance.Contrast(img).enhance(0.9)
        elif filter_id == "low_key":
            img = ImageEnhance.Brightness(img).enhance(0.8)
            img = ImageEnhance.Contrast(img).enhance(1.3 * intensity)
        elif filter_id == "sharpen":
            for _ in range(int(intensity)):
                img = img.filter(ImageFilter.SHARPEN)
        elif filter_id == "denoise":
            img = img.filter(ImageFilter.SMOOTH)
        elif filter_id == "dehaze":
            img = self._dehaze_effect(img, intensity)
        elif filter_id == "vignette":
            img = self._vignette_effect(img, intensity, params.get("size", 0.5))
        elif filter_id == "glow":
            img = img.filter(ImageFilter.GaussianBlur(radius=params.get("radius", 10)))
            img = ImageEnhance.Brightness(img).enhance(1.2)
        
        return img
    
    def _apply_glitch_filter(
        self,
        image: Image.Image,
        filter_id: str,
        intensity: float,
        **params,
    ) -> Image.Image:
        """Apply glitch/digital effect filters."""
        img = np.array(image)
        
        if filter_id == "glitch":
            img = self._glitch_effect(img, intensity)
        elif filter_id == "scanlines":
            img = self._scanlines_effect(img, intensity, params.get("count", 200))
        elif filter_id == "static":
            img = self._static_effect(img, intensity)
        elif filter_id == "rgb_shift":
            img = self._rgb_shift_effect(img, intensity, params.get("amount", 5))
        elif filter_id == "chromatic":
            img = self._chromatic_effect(img, intensity)
        elif filter_id == "pixelate":
            img = self._pixelate_effect(img, intensity, params.get("block_size", 8))
        elif filter_id == "mosaic":
            img = self._mosaic_effect(img, intensity, params.get("tile_size", 16))
        elif filter_id == "corruption":
            img = self._corruption_effect(img, intensity)
        
        return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    
    def _apply_vintage_filter(
        self,
        image: Image.Image,
        filter_id: str,
        intensity: float,
        **params,
    ) -> Image.Image:
        """Apply vintage/retro filters."""
        img = image.copy()
        
        if filter_id == "faded_photo":
            img = self._faded_effect(img, intensity)
        elif filter_id == "polaroid":
            img = self._polaroid_effect(img, intensity)
        elif filter_id == "kodachrome":
            img = self._kodachrome_effect(img, intensity)
        elif filter_id == "ektachrome":
            img = self._ektachrome_effect(img, intensity)
        elif filter_id in ["bw_agfa", "bw_kodak"]:
            img = self._bw_effect(img, intensity, warm=filter_id == "bw_kodak")
        elif filter_id == "light_leak":
            img = self._light_leak_effect(img, intensity, params.get("color", "orange"))
        elif filter_id == "film_grain":
            img = self._film_grain_effect(img, intensity, params.get("size", 1.5))
        elif filter_id == "dust":
            img = self._dust_effect(img, intensity)
        elif filter_id == "halftone":
            img = self._halftone_effect(img, intensity, params.get("dot_size", 4))
        elif filter_id == "infrared":
            img = self._infrared_effect(img, intensity)
        elif filter_id == "toy_camera":
            img = self._toy_camera_effect(img, intensity)
        
        return img
    
    # ─────────────────────────────────────────────────────────────────────────────
    # HELPER EFFECTS
    # ─────────────────────────────────────────────────────────────────────────────
    
    def _vintage_effect(self, img: Image.Image, intensity: float) -> Image.Image:
        """Vintage film effect."""
        # Slightly desaturate
        img = ImageEnhance.Color(img).enhance(0.9)
        # Add warmth
        img = ImageEnhance.Brightness(img).enhance(0.95)
        # Reduce contrast slightly
        img = ImageEnhance.Contrast(img).enhance(0.95)
        # Add grain
        img = self._film_grain_effect(img, 0.2 * intensity)
        return img
    
    def _cinematic_effect(self, img: Image.Image, intensity: float) -> Image.Image:
        """Cinematic color grading - teal shadows, orange highlights."""
        img_array = np.array(img).astype(np.float32)
        
        # Split channels
        r, g, b = img_array[:,:,0], img_array[:,:,1], img_array[:,:,2]
        
        # Calculate luminance
        lum = 0.299 * r + 0.587 * g + 0.114 * b
        
        # Teal in shadows
        shadow_mask = np.clip(1 - lum / 128, 0, 1)
        r = np.clip(r + 10 * shadow_mask * intensity, 0, 255)
        b = np.clip(b + 30 * shadow_mask * intensity, 0, 255)
        
        # Orange in highlights
        highlight_mask = np.clip(lum / 128 - 1, 0, 1)
        r = np.clip(r + 20 * highlight_mask * intensity, 0, 255)
        g = np.clip(g + 10 * highlight_mask * intensity, 0, 255)
        
        return Image.fromarray(np.stack([r, g, b], axis=2).astype(np.uint8))
    
    def _sepia_effect(self, img: Image.Image, intensity: float) -> Image.Image:
        """Sepia tone effect."""
        img_array = np.array(img)
        
        # Sepia matrix
        sepia_matrix = np.array([
            [0.393, 0.769, 0.189],
            [0.349, 0.686, 0.168],
            [0.272, 0.534, 0.131],
        ])
        
        sepia = np.clip(np.tensordot(img_array, sepia_matrix.T, axes=1), 0, 255)
        
        # Blend with original
        result = img_array * (1 - intensity) + sepia * intensity
        
        return Image.fromarray(result.astype(np.uint8))
    
    def _neon_effect(self, img: Image.Image, intensity: float, color: str) -> Image.Image:
        """Neon glow effect."""
        colors = {
            "cyan": (0, 255, 255),
            "pink": (255, 0, 255),
            "blue": (0, 100, 255),
            "purple": (128, 0, 255),
        }
        glow_color = colors.get(color, colors["cyan"])
        
        # Convert to array
        img_array = np.array(img).astype(np.float32)
        
        # Add glow to bright areas
        lum = 0.299 * img_array[:,:,0] + 0.587 * img_array[:,:,1] + 0.114 * img_array[:,:,2]
        glow_mask = np.clip(lum / 100, 0, 1) * intensity
        
        for i, c in enumerate(glow_color):
            img_array[:,:,i] = np.clip(img_array[:,:,i] + c * glow_mask * 0.3, 0, 255)
        
        # Boost saturation
        hsv = self._rgb_to_hsv(img_array)
        hsv[:,:,1] = np.clip(hsv[:,:,1] * 1.5, 0, 1)
        img_array = self._hsv_to_rgb(hsv)
        
        return Image.fromarray(img_array.astype(np.uint8))
    
    def _sketch_effect(self, img: Image.Image, intensity: float) -> Image.Image:
        """Pencil sketch effect."""
        gray = ImageOps.grayscale(img)
        gray_array = np.array(gray).astype(np.float32)
        
        # Edge detection
        edges = cv2.Canny(gray_array.astype(np.uint8), 50, 150)
        
        # Invert
        sketch = 255 - edges
        
        # Blend with original
        result = gray.point(lambda x: x * (1 - 0.5 * intensity))
        
        return result.convert("RGB")
    
    def _comic_effect(self, img: Image.Image, intensity: float) -> Image.Image:
        """Comic book effect."""
        # Increase saturation
        img = ImageEnhance.Color(img).enhance(1.5 * intensity)
        # Edge enhancement
        img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)
        # Posterize
        img = ImageOps.posterize(img, int(6 - 2 * intensity))
        
        return img
    
    def _holographic_effect(self, img: Image.Image, intensity: float) -> Image.Image:
        """Holographic shimmer effect."""
        img_array = np.array(img).astype(np.float32)
        h, w = img_array.shape[:2]
        
        # Create shifting color bands
        x = np.arange(w) / w
        y = np.arange(h) / h
        xx, yy = np.meshgrid(x, y)
        
        shift = np.sin((xx + yy) * 10) * 0.1 * intensity
        
        r_shift = (shift * 2).astype(int) % 3
        g_shift = ((shift + 0.33) * 2).astype(int) % 3
        b_shift = ((shift + 0.66) * 2).astype(int) % 3
        
        result = img_array.copy()
        for i in range(3):
            result[:,:,i] = np.roll(img_array[:,:,r_shift[i]], int(shift[i] * 10), axis=i)
        
        # Add shimmer
        shimmer = np.sin((xx + yy) * 20) * 30 * intensity
        result = np.clip(result + shimmer[:,:,None], 0, 255)
        
        return Image.fromarray(result.astype(np.uint8))
    
    def _chrome_effect(self, img: Image.Image, intensity: float) -> Image.Image:
        """Chrome/metallic effect."""
        img_array = np.array(img).astype(np.float32)
        
        # High contrast
        img_array = np.clip((img_array - 128) * 2 + 128, 0, 255)
        
        # Add metallic sheen
        lum = 0.299 * img_array[:,:,0] + 0.587 * img_array[:,:,1] + 0.114 * img_array[:,:,2]
        sheen = np.sin(lum / 50) * 50 * intensity
        
        for i in range(3):
            img_array[:,:,i] = np.clip(img_array[:,:,i] + sheen, 0, 255)
        
        return Image.fromarray(img_array.astype(np.uint8))
    
    def _vaporwave_effect(self, img: Image.Image, intensity: float) -> Image.Image:
        """Vaporwave aesthetic."""
        img_array = np.array(img).astype(np.float32)
        
        # Pink-blue gradient
        h, w = img_array.shape[:2]
        gradient = np.linspace(0, 1, h)[:, None, None]
        
        img_array[:,:,0] = np.clip(img_array[:,:,0] + gradient[:,:,0] * 50 * intensity, 0, 255)  # R
        img_array[:,:,2] = np.clip(img_array[:,:,2] + (1 - gradient[:,:,0]) * 50 * intensity, 0, 255)  # B
        
        # Desaturate
        hsv = self._rgb_to_hsv(img_array)
        hsv[:,:,1] = np.clip(hsv[:,:,1] * 0.7, 0, 1)
        img_array = self._hsv_to_rgb(hsv)
        
        return Image.fromarray(img_array.astype(np.uint8))
    
    def _synthwave_effect(self, img: Image.Image, intensity: float) -> Image.Image:
        """Synthwave/retrowave effect."""
        img_array = np.array(img).astype(np.float32)
        
        # Sunset colors
        h, w = img_array.shape[:2]
        gradient = np.linspace(0, 1, h)[:, None, None]
        
        # Orange in lower half, purple in upper
        img_array[:,:,0] = np.clip(img_array[:,:,0] * (1 + gradient[:,:,0] * 0.5 * intensity), 0, 255)
        img_array[:,:,2] = np.clip(img_array[:,:,2] + (1 - gradient[:,:,0]) * 80 * intensity, 0, 255)
        
        # Increase saturation in lower portion
        hsv = self._rgb_to_hsv(img_array)
        hsv[:,:,1] = np.where(gradient[:,:,0] > 0.5, hsv[:,:,1] * 1.3, hsv[:,:,1])
        img_array = self._hsv_to_rgb(hsv)
        
        return Image.fromarray(img_array.astype(np.uint8))
    
    def _teal_orange_effect(self, img: Image.Image, intensity: float) -> Image.Image:
        """Teal and orange color grading."""
        return self._cinematic_effect(img, intensity)
    
    def _golden_hour_effect(self, img: Image.Image, intensity: float) -> Image.Image:
        """Golden hour warmth effect."""
        img_array = np.array(img).astype(np.float32)
        
        # Add warmth
        img_array[:,:,0] = np.clip(img_array[:,:,0] * (1 + 0.2 * intensity), 0, 255)  # R
        img_array[:,:,1] = np.clip(img_array[:,:,1] * (1 + 0.1 * intensity), 0, 255)  # G
        img_array[:,:,2] = np.clip(img_array[:,:,2] * (1 - 0.1 * intensity), 0, 255)  # B
        
        return Image.fromarray(img_array.astype(np.uint8))
    
    def _cool_blue_effect(self, img: Image.Image, intensity: float) -> Image.Image:
        """Cool blue tones effect."""
        img_array = np.array(img).astype(np.float32)
        
        # Cool shift
        img_array[:,:,0] = np.clip(img_array[:,:,0] * (1 - 0.15 * intensity), 0, 255)  # R
        img_array[:,:,2] = np.clip(img_array[:,:,2] * (1 + 0.2 * intensity), 0, 255)  # B
        
        return Image.fromarray(img_array.astype(np.uint8))
    
    def _duotone_effect(
        self,
        img: Image.Image,
        shadow_color: str,
        highlight_color: str,
        intensity: float,
    ) -> Image.Image:
        """Duotone effect with two colors."""
        gray = ImageOps.grayscale(img)
        gray_array = np.array(gray) / 255
        
        # Parse colors
        from PIL import ImageColor
        shadow = np.array(ImageColor.getrgb(shadow_color))
        highlight = np.array(ImageColor.getrgb(highlight_color))
        
        # Interpolate between colors based on grayscale value
        result = shadow * (1 - gray_array[:,:,None]) + highlight * gray_array[:,:,None]
        
        # Blend with original based on intensity
        img_array = np.array(img).astype(np.float32)
        result = img_array * (1 - intensity) + result * intensity
        
        return Image.fromarray(result.clip(0, 255).astype(np.uint8))
    
    def _color_splash_effect(
        self,
        img: Image.Image,
        target_color: str,
        intensity: float,
    ) -> Image.Image:
        """Keep only one color, grayscale rest."""
        img_array = np.array(img).astype(np.float32)
        gray = 0.299 * img_array[:,:,0] + 0.587 * img_array[:,:,1] + 0.114 * img_array[:,:,2]
        gray_img = np.stack([gray, gray, gray], axis=2)
        
        # Determine which pixels are the target color
        if target_color == "red":
            mask = (img_array[:,:,0] > 100) & (img_array[:,:,1] < 80) & (img_array[:,:,2] < 80)
        elif target_color == "blue":
            mask = (img_array[:,:,2] > 100) & (img_array[:,:,0] < 80) & (img_array[:,:,1] < 80)
        elif target_color == "green":
            mask = (img_array[:,:,1] > 80) & (img_array[:,:,0] < 80) & (img_array[:,:,2] < 80)
        else:
            mask = (img_array[:,:,0] > 100) & (img_array[:,:,1] > 100) & (img_array[:,:,2] < 80)
        
        mask = mask[:,:,None]
        
        result = gray_img * (1 - mask * intensity) + img_array * mask * intensity
        
        return Image.fromarray(result.astype(np.uint8))
    
    def _color_pop_effect(
        self,
        img: Image.Image,
        target_color: str,
        intensity: float,
    ) -> Image.Image:
        """Pop one color out, desaturate others."""
        img_array = np.array(img).astype(np.float32)
        
        # Simple grayscale conversion for non-target
        gray = 0.299 * img_array[:,:,0] + 0.587 * img_array[:,:,1] + 0.114 * img_array[:,:,2]
        gray_img = np.stack([gray, gray, gray], axis=2)
        
        # Desaturate
        result = img_array * (1 - 0.8 * intensity) + gray_img * 0.8 * intensity
        
        return Image.fromarray(result.astype(np.uint8))
    
    def _hdr_effect(self, img: Image.Image, intensity: float) -> Image.Image:
        """HDR effect - enhance dynamic range."""
        img_array = np.array(img).astype(np.float32)
        
        # Enhance local contrast
        for _ in range(int(intensity)):
            blurred = cv2.GaussianBlur(img_array, (35, 35), 0)
            detail = img_array - blurred
            img_array = img_array + detail * 0.5
        
        # Boost saturation slightly
        hsv = self._rgb_to_hsv(img_array)
        hsv[:,:,1] = np.clip(hsv[:,:,1] * 1.2, 0, 1)
        img_array = self._hsv_to_rgb(hsv)
        
        return Image.fromarray(np.clip(img_array, 0, 255).astype(np.uint8))
    
    def _clarity_effect(self, img: Image.Image, intensity: float) -> Image.Image:
        """Clarity effect - midtone contrast."""
        img_array = np.array(img).astype(np.float32)
        
        # Unsharp mask on midtones
        blurred = cv2.GaussianBlur(img_array, (75, 75), 0)
        detail = img_array - blurred
        
        # Only enhance midtones
        lum = 0.299 * img_array[:,:,0] + 0.587 * img_array[:,:,1] + 0.114 * img_array[:,:,2]
        midtone_mask = 1 - np.abs(lum - 128) / 128
        
        enhanced = img_array + detail * midtone_mask[:,:,None] * intensity * 0.5
        
        return Image.fromarray(np.clip(enhanced, 0, 255).astype(np.uint8))
    
    def _dehaze_effect(self, img: Image.Image, intensity: float) -> Image.Image:
        """Dehaze effect - reduce fog/haze."""
        img_array = np.array(img).astype(np.float32)
        
        # Estimate haze (usually in upper portion)
        top_portion = img_array[:img_array.shape[0]//3]
        haze_color = np.median(top_portion.reshape(-1, 3), axis=0)
        
        # Remove haze
        img_array = img_array - haze_color * 0.3 * intensity
        
        return Image.fromarray(np.clip(img_array, 0, 255).astype(np.uint8))
    
    def _vignette_effect(
        self,
        img: Image.Image,
        intensity: float,
        size: float,
    ) -> Image.Image:
        """Vignette effect - darken edges."""
        img_array = np.array(img).astype(np.float32)
        h, w = img_array.shape[:2]
        
        # Create vignette mask
        y, x = np.ogrid[:h, :w]
        center_y, center_x = h // 2, w // 2
        
        dist = np.sqrt((x - center_x)**2 + (y - center_y)**2)
        max_dist = np.sqrt(center_x**2 + center_y**2)
        
        vignette = 1 - np.clip((dist / (max_dist * size))**2 * intensity, 0, 1)
        
        # Apply vignette
        img_array = img_array * vignette[:,:,None]
        
        return Image.fromarray(np.clip(img_array, 0, 255).astype(np.uint8))
    
    def _glitch_effect(self, img: np.ndarray, intensity: float) -> np.ndarray:
        """Glitch effect - digital corruption."""
        h, w = img.shape[:2]
        result = img.copy()
        
        # Horizontal displacement
        num_slices = int(20 * intensity)
        for _ in range(num_slices):
            y = np.random.randint(0, h)
            slice_h = np.random.randint(1, 20)
            shift = np.random.randint(-50, 50) * intensity
            
            if y + slice_h < h:
                result[y:y+slice_h] = np.roll(
                    result[y:y+slice_h], int(shift), axis=1
                )
        
        # RGB split
        shift = int(5 * intensity)
        result[:,:,0] = np.roll(result[:,:,0], shift, axis=1)
        result[:,:,2] = np.roll(result[:,:,2], -shift, axis=1)
        
        return result
    
    def _scanlines_effect(
        self,
        img: np.ndarray,
        intensity: float,
        count: int,
    ) -> np.ndarray:
        """Scanlines effect."""
        result = img.copy()
        h = img.shape[0]
        
        for i in range(0, h, max(1, int(h / count))):
            alpha = 0.3 * intensity
            result[i:i+1,:] = result[i:i+1,:] * (1 - alpha)
        
        return result
    
    def _static_effect(self, img: np.ndarray, intensity: float) -> np.ndarray:
        """Static noise effect."""
        noise = np.random.randint(0, 255, img.shape, dtype=np.uint8)
        return np.clip(
            img * (1 - 0.3 * intensity) + noise * 0.3 * intensity,
            0, 255
        ).astype(np.uint8)
    
    def _rgb_shift_effect(
        self,
        img: np.ndarray,
        intensity: float,
        amount: int,
    ) -> np.ndarray:
        """RGB channel shift effect."""
        result = img.copy()
        shift = int(amount * intensity)
        
        result[:,:,0] = np.roll(img[:,:,0], shift, axis=1)  # R
        result[:,:,1] = np.roll(img[:,:,1], shift // 2, axis=1)  # G
        result[:,:,2] = np.roll(img[:,:,2], -shift, axis=1)  # B
        
        return result
    
    def _chromatic_effect(self, img: np.ndarray, intensity: float) -> np.ndarray:
        """Chromatic aberration effect."""
        return self._rgb_shift_effect(img, intensity, 10)
    
    def _pixelate_effect(
        self,
        img: np.ndarray,
        intensity: float,
        block_size: int,
    ) -> np.ndarray:
        """Pixelate effect."""
        h, w = img.shape[:2]
        size = max(1, int(block_size * intensity))
        
        # Downsample then upsample
        small_h, small_w = h // size, w // size
        small = img.reshape(small_h, size, small_w, size, 3).mean(axis=(1, 3))
        result = np.repeat(np.repeat(small, size, axis=0), size, axis=1)
        
        return result[:h, :w]
    
    def _mosaic_effect(
        self,
        img: np.ndarray,
        intensity: float,
        tile_size: int,
    ) -> np.ndarray:
        """Mosaic effect."""
        return self._pixelate_effect(img, intensity, tile_size)
    
    def _corruption_effect(self, img: np.ndarray, intensity: float) -> np.ndarray:
        """Data corruption effect."""
        result = img.copy()
        h, w = img.shape[:2]
        
        # Random block corruptions
        num_corruptions = int(30 * intensity)
        for _ in range(num_corruptions):
            y, x = np.random.randint(0, h), np.random.randint(0, w)
            bh, bw = np.random.randint(5, 30), np.random.randint(5, 30)
            
            if y + bh < h and x + bw < w:
                # Fill with random or shifted data
                if np.random.random() > 0.5:
                    result[y:y+bh, x:x+bw] = np.random.randint(0, 255, (bh, bw, 3), dtype=np.uint8)
                else:
                    result[y:y+bh, x:x+bw] = np.roll(
                        img[y:y+bh, x:x+bw],
                        np.random.randint(-20, 20),
                        axis=0
                    )
        
        return result
    
    def _faded_effect(self, img: Image.Image, intensity: float) -> Image.Image:
        """Faded photo effect."""
        img_array = np.array(img).astype(np.float32)
        
        # Add haze/whiteness
        img_array = img_array * (1 - 0.15 * intensity) + 255 * 0.15 * intensity
        
        # Reduce contrast
        img_array = (img_array - 128) * (1 - 0.2 * intensity) + 128
        
        # Slight yellow tint
        img_array[:,:,0] = img_array[:,:,0] * (1 + 0.05 * intensity)  # R
        img_array[:,:,2] = img_array[:,:,2] * (1 - 0.1 * intensity)  # B
        
        return Image.fromarray(np.clip(img_array, 0, 255).astype(np.uint8))
    
    def _polaroid_effect(self, img: Image.Image, intensity: float) -> Image.Image:
        """Polaroid instant photo effect."""
        w, h = img.size
        border = 20
        
        # Add white border
        new_w, new_h = w + border * 2, h + border * 4
        result = Image.new("RGB", (new_w, new_h), (255, 255, 255))
        result.paste(img, (border, border))
        
        # Slight fade and warm tone
        result = self._faded_effect(result, 0.3 * intensity)
        result = ImageEnhance.Brightness(result).enhance(0.95)
        
        return result
    
    def _kodachrome_effect(self, img: Image.Image, intensity: float) -> Image.Image:
        """Kodachrome film colors."""
        img_array = np.array(img).astype(np.float32)
        
        # Boost reds and oranges, deepen blues
        img_array[:,:,0] = np.clip(img_array[:,:,0] * (1 + 0.2 * intensity), 0, 255)
        img_array[:,:,1] = np.clip(img_array[:,:,1] * (1 + 0.15 * intensity), 0, 255)
        img_array[:,:,2] = np.clip(img_array[:,:,2] * (1 - 0.1 * intensity), 0, 255)
        
        # High saturation
        hsv = self._rgb_to_hsv(img_array)
        hsv[:,:,1] = np.clip(hsv[:,:,1] * 1.3, 0, 1)
        img_array = self._hsv_to_rgb(hsv)
        
        return Image.fromarray(img_array.astype(np.uint8))
    
    def _ektachrome_effect(self, img: Image.Image, intensity: float) -> Image.Image:
        """Ektachrome slide film - vibrant, cooler."""
        img_array = np.array(img).astype(np.float32)
        
        # Slight cyan in shadows
        lum = 0.299 * img_array[:,:,0] + 0.587 * img_array[:,:,1] + 0.114 * img_array[:,:,2]
        shadow_mask = np.clip(1 - lum / 100, 0, 1)
        
        img_array[:,:,2] = np.clip(img_array[:,:,2] + 30 * shadow_mask * intensity, 0, 255)
        
        # High saturation
        hsv = self._rgb_to_hsv(img_array)
        hsv[:,:,1] = np.clip(hsv[:,:,1] * 1.4, 0, 1)
        img_array = self._hsv_to_rgb(hsv)
        
        return Image.fromarray(img_array.astype(np.uint8))
    
    def _bw_effect(self, img: Image.Image, intensity: float, warm: bool = False) -> Image.Image:
        """Black and white effect."""
        gray = ImageOps.grayscale(img)
        result = ImageEnhance.Contrast(gray).enhance(1.2)
        
        if warm:
            # Slight sepia tint
            result = np.array(result)
            result = np.stack([
                result * 1.1,
                result * 1.0,
                result * 0.9,
            ], axis=2).clip(0, 255).astype(np.uint8)
            result = Image.fromarray(result)
        
        return result.convert("RGB")
    
    def _light_leak_effect(
        self,
        img: Image.Image,
        intensity: float,
        color: str,
    ) -> Image.Image:
        """Light leak effect."""
        img_array = np.array(img).astype(np.float32)
        h, w = img_array.shape[:2]
        
        # Create gradient leak
        y = np.arange(h) / h
        leak = np.sin(y * np.pi)[:, None, None] * intensity * 100
        
        colors = {
            "orange": (255, 150, 50),
            "red": (255, 50, 50),
            "pink": (255, 100, 150),
            "yellow": (255, 255, 100),
        }
        leak_color = colors.get(color, colors["orange"])
        
        for i, c in enumerate(leak_color):
            img_array[:,:,i] = np.clip(img_array[:,:,i] + leak[:,:,0] * c / 255 * 0.5, 0, 255)
        
        return Image.fromarray(img_array.astype(np.uint8))
    
    def _film_grain_effect(
        self,
        img: Image.Image,
        intensity: float,
        size: float,
    ) -> Image.Image:
        """Film grain effect."""
        img_array = np.array(img).astype(np.float32)
        
        # Generate grain
        grain = np.random.normal(0, 10 * intensity, img_array.shape) * size
        
        # Apply grain
        img_array = img_array + grain
        
        return Image.fromarray(np.clip(img_array, 0, 255).astype(np.uint8))
    
    def _dust_effect(self, img: Image.Image, intensity: float) -> Image.Image:
        """Dust and scratches effect."""
        img_array = np.array(img).astype(np.float32)
        h, w = img_array.shape[:2]
        
        # Add dust particles
        dust_count = int(100 * intensity)
        for _ in range(dust_count):
            x, y = np.random.randint(0, w), np.random.randint(0, h)
            size = np.random.randint(1, 3)
            brightness = np.random.randint(-50, -20)
            
            if x + size < w and y + size < h:
                img_array[y:y+size, x:x+size] = np.clip(
                    img_array[y:y+size, x:x+size] + brightness,
                    0, 255
                )
        
        # Add random scratches
        scratch_count = int(5 * intensity)
        for _ in range(scratch_count):
            x = np.random.randint(0, w)
            length = np.random.randint(20, 100)
            brightness = np.random.randint(-80, -30)
            
            y_start = np.random.randint(0, h)
            y_end = min(y_start + length, h)
            
            img_array[y_start:y_end, x] = np.clip(
                img_array[y_start:y_end, x] + brightness,
                0, 255
            )
        
        return Image.fromarray(img_array.astype(np.uint8))
    
    def _halftone_effect(
        self,
        img: Image.Image,
        intensity: float,
        dot_size: int,
    ) -> Image.Image:
        """Halftone print effect."""
        gray = np.array(ImageOps.grayscale(img))
        h, w = gray.shape
        
        # Downsample to halftone grid
        small_h, small_w = h // dot_size, w // dot_size
        small = gray[:small_h * dot_size, :small_w * dot_size].reshape(
            small_h, dot_size, small_w, dot_size
        ).mean(axis=(1, 3))
        
        # Create dots
        dots = (small / 255 * dot_size**2).astype(int).clip(0, dot_size**2)
        halftone = (dots / dot_size**2 * 255).astype(np.uint8)
        
        # Upscale back
        result = np.repeat(np.repeat(halftone, dot_size, axis=0), dot_size, axis=1)
        
        return Image.fromarray(result).convert("RGB")
    
    def _infrared_effect(self, img: Image.Image, intensity: float) -> Image.Image:
        """Fake infrared photo effect."""
        img_array = np.array(img).astype(np.float32)
        
        # Swap channels for infrared look
        r, g, b = img_array[:,:,0].copy(), img_array[:,:,1].copy(), img_array[:,:,2].copy()
        
        # Grass becomes bright, sky becomes cyan
        img_array[:,:,0] = np.clip(r * 0.3 + g * 0.5, 0, 255)  # New R
        img_array[:,:,1] = np.clip(r * 0.6 + g * 0.3 + b * 0.1, 0, 255)  # New G
        img_array[:,:,2] = np.clip(g * 0.5 + b * 0.5, 0, 255)  # New B
        
        return Image.fromarray(img_array.astype(np.uint8))
    
    def _toy_camera_effect(self, img: Image.Image, intensity: float) -> Image.Image:
        """Toy camera/lomo effect."""
        img = self._vignette_effect(img, 0.5 * intensity, 0.6)
        img = self._faded_effect(img, 0.3 * intensity)
        img = ImageEnhance.Color(img).enhance(1.2)
        
        # Random color shift
        if np.random.random() > 0.5:
            img = self._light_leak_effect(img, 0.2 * intensity, "orange")
        
        return img
    
    def _rgb_to_hsv(self, rgb: np.ndarray) -> np.ndarray:
        """Convert RGB to HSV."""
        rgb = rgb / 255.0
        r, g, b = rgb[:,:,0], rgb[:,:,1], rgb[:,:,2]
        
        maxc = np.maximum(r, np.maximum(g, b))
        minc = np.minimum(r, np.minimum(g, b))
        v = maxc
        
        s = np.where(maxc != 0, (maxc - minc) / maxc, 0)
        
        delta = maxc - minc
        delta = np.where(delta == 0, 1e-10, delta)
        
        h = np.zeros_like(delta)
        mask_r = (maxc == r) & (delta != 0)
        mask_g = (maxc == g) & (delta != 0)
        mask_b = (maxc == b) & (delta != 0)
        
        h[mask_r] = ((g[mask_r] - b[mask_r]) / delta[mask_r]) % 6
        h[mask_g] = ((b[mask_g] - r[mask_g]) / delta[mask_g]) + 2
        h[mask_b] = ((r[mask_b] - g[mask_b]) / delta[mask_b]) + 4
        
        h = h / 6.0
        
        return np.stack([h, s, v], axis=2)
    
    def _hsv_to_rgb(self, hsv: np.ndarray) -> np.ndarray:
        """Convert HSV to RGB."""
        h, s, v = hsv[:,:,0], hsv[:,:,1], hsv[:,:,2]
        
        i = (h * 6.0).astype(int)
        f = (h * 6.0) - i
        p = v * (1 - s)
        q = v * (1 - f * s)
        t = v * (1 - (1 - f) * s)
        
        i = i % 6
        
        result = np.zeros_like(hsv)
        
        for idx in range(6):
            mask = i == idx
            result[:,:,0][mask] = np.where(mask, [v, t, p, p, t, v][idx], result[:,:,0][mask])
            result[:,:,1][mask] = np.where(mask, [q, v, v, t, p, p][idx], result[:,:,1][mask])
            result[:,:,2][mask] = np.where(mask, [p, p, q, v, v, t][idx], result[:,:,2][mask])
        
        return result * 255
    
    async def save_filtered_image(
        self,
        image: Image.Image,
        filter_id: str,
    ) -> dict:
        """Apply filter and save to outputs."""
        filtered = await self.apply_filter(image, filter_id)
        
        img_id = str(uuid.uuid4())
        output_path = settings.OUTPUTS_DIR / f"{img_id}.png"
        filtered.save(output_path, "PNG")
        
        return {
            "id": img_id,
            "path": str(output_path),
            "filter": filter_id,
        }


# Global instance
filter_service = FilterService()
