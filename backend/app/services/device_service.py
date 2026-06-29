"""
DolphinPhoto AI Studio - Device Service
Hardware detection and optimization
"""
from __future__ import annotations

import os
import platform
from dataclasses import dataclass, field

try:
    import psutil
except ImportError:
    psutil = None


@dataclass
class DeviceInfo:
    """Device hardware information."""
    device_name: str = "Unknown"
    device_type: str = "cpu"  # cuda, mps, cpu
    device: str = "cpu"
    ram_gb: float = 0.0
    vram_gb: float | None = None
    vram_total: int | None = None
    vram_available: int | None = None
    cpu_count: int = 0
    cpu_brand: str = "Unknown"
    performance_tier: str = "unknown"
    cuda_available: bool = False
    cuda_version: str | None = None
    mps_available: bool = False
    os_name: str = "Unknown"
    os_version: str = "Unknown"


class DeviceService:
    """Service for device detection and hardware info."""
    
    _info: DeviceInfo | None = None
    
    def __init__(self):
        self._detect_hardware()
    
    @property
    def info(self) -> DeviceInfo:
        """Get cached device information."""
        return self._info
    
    def _detect_hardware(self) -> None:
        """Detect available hardware."""
        info = DeviceInfo()
        
        # OS Info
        info.os_name = platform.system()
        info.os_version = platform.release()
        
        # CPU Info
        info.cpu_count = psutil.cpu_count(logical=False) if psutil else os.cpu_count() or 1
        try:
            info.cpu_brand = platform.processor() or "Unknown"
        except Exception:
            info.cpu_brand = "Unknown"
        
        # RAM Info
        if psutil:
            mem = psutil.virtual_memory()
            info.ram_gb = round(mem.total / (1024**3), 2)
        else:
            info.ram_gb = 0.0
        
        # Device Type Detection
        info.device = "cpu"
        info.device_type = "cpu"
        info.device_name = f"CPU ({info.cpu_brand[:20]})"
        
        # CUDA Detection
        info.cuda_available = self._check_cuda()
        if info.cuda_available:
            info.device = "cuda"
            info.device_type = "cuda"
            info.cuda_version = self._get_cuda_version()
            info.device_name = self._get_gpu_name()
            info.vram_total, info.vram_available = self._get_vram_info()
            if info.vram_total:
                info.vram_gb = round(info.vram_total / (1024**3), 2)
        
        # MPS Detection (Apple Silicon)
        elif self._check_mps():
            info.device = "mps"
            info.device_type = "mps"
            info.mps_available = True
            info.device_name = "Apple Silicon (MPS)"
            # Estimate MPS memory
            info.vram_gb = min(info.ram_gb * 0.75, 64)
        
        # Performance Tier
        info.performance_tier = self._calculate_tier(info)
        
        self._info = info
    
    def _check_cuda(self) -> bool:
        """Check if CUDA is available."""
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False
    
    def _get_cuda_version(self) -> str | None:
        """Get CUDA version."""
        try:
            import torch
            if torch.cuda.is_available():
                return torch.version.cuda
        except Exception:
            pass
        return None
    
    def _get_gpu_name(self) -> str:
        """Get GPU name."""
        try:
            import torch
            if torch.cuda.is_available():
                return torch.cuda.get_device_name(0)
        except Exception:
            pass
        return "NVIDIA GPU"
    
    def _get_vram_info(self) -> tuple[int, int] | None:
        """Get VRAM info in bytes."""
        try:
            import torch
            if torch.cuda.is_available():
                total = torch.cuda.get_device_properties(0).total_memory
                available = total - torch.cuda.memory_allocated(0)
                return int(total), int(available)
        except Exception:
            pass
        return None
    
    def _check_mps(self) -> bool:
        """Check if MPS (Metal Performance Shaders) is available."""
        try:
            import torch
            return torch.backends.mps.is_available()
        except Exception:
            return False
    
    def _calculate_tier(self, info: DeviceInfo) -> str:
        """Calculate performance tier based on hardware."""
        vram = info.vram_gb or 0
        ram = info.ram_gb
        
        if info.device == "cuda" and vram >= 24:
            return "🔥 Elite (24GB+ VRAM)"
        elif info.device == "cuda" and vram >= 16:
            return "⚡ Premium (16GB VRAM)"
        elif info.device == "cuda" and vram >= 8:
            return "💪 High (8GB VRAM)"
        elif info.device == "cuda" and vram >= 4:
            return "✨ Mid (4GB VRAM)"
        elif info.device == "mps":
            return "🍎 Apple Silicon"
        elif ram >= 32:
            return "💻 High-End CPU"
        elif ram >= 16:
            return "📊 Mid-Range CPU"
        else:
            return "⚠️ Entry Level"
    
    def get_optimal_settings(self) -> dict:
        """Get optimal settings for current device."""
        info = self._info
        if not info:
            return {"batch_size": 1, "precision": "fp32", "optimize_memory": True}
        
        if info.device == "cuda":
            if (info.vram_gb or 0) >= 16:
                return {
                    "batch_size": 4,
                    "precision": "fp16",
                    "optimize_memory": False,
                    "attention_slicing": False,
                    "vae_slicing": False,
                }
            elif (info.vram_gb or 0) >= 8:
                return {
                    "batch_size": 2,
                    "precision": "fp16",
                    "optimize_memory": True,
                    "attention_slicing": True,
                    "vae_slicing": True,
                }
            else:
                return {
                    "batch_size": 1,
                    "precision": "fp16",
                    "optimize_memory": True,
                    "attention_slicing": True,
                    "vae_slicing": True,
                }
        elif info.device == "mps":
            return {
                "batch_size": 1,
                "precision": "fp16",
                "optimize_memory": True,
                "attention_slicing": True,
                "vae_slicing": True,
            }
        else:
            return {
                "batch_size": 1,
                "precision": "fp32",
                "optimize_memory": True,
                "attention_slicing": True,
                "vae_slicing": True,
            }


# Global instance
device_service = DeviceService()
