"""
DolphinPhoto AI Studio - Configuration Management
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )

    # ── Application Info ─────────────────────────────────────────────────────────
    APP_NAME: str = "DolphinPhoto AI Studio"
    COMPANY: str = "Black Tiger Computing"
    LEAD_DEV: str = "Sona McGoo"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "The Ultimate AI Creative Studio"

    # ── Server ─────────────────────────────────────────────────────────────────
    HOST: str = "127.0.0.1"
    PORT: int = 7777
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False

    # ── Workspace ───────────────────────────────────────────────────────────────
    WORKSPACE_DIR: Path = Path.home() / ".dolphinphoto"
    MODELS_DIR: Path = WORKSPACE_DIR / "models"
    OUTPUTS_DIR: Path = WORKSPACE_DIR / "outputs"
    WORKFLOWS_DIR: Path = WORKSPACE_DIR / "workflows"
    TEMP_DIR: Path = WORKSPACE_DIR / "temp"
    PROJECTS_DIR: Path = WORKSPACE_DIR / "projects"
    CACHE_DIR: Path = WORKSPACE_DIR / "cache"
    
    SETUP_COMPLETE: bool = False
    
    # ── AI Configuration ────────────────────────────────────────────────────────
    DEVICE: Literal["cuda", "mps", "cpu"] = "cpu"
    HF_TOKEN: str | None = None
    CIVITAI_API_KEY: str | None = None
    
    # ── Model Settings ─────────────────────────────────────────────────────────
    DEFAULT_MODEL: str = "stabilityai/stable-diffusion-2-1"
    DEFAULT_VAE: str | None = None
    SAFETY_CHECKER: bool = True
    ATTENTION_SLICE: bool = True
    VAE_SLICE: bool = True
    
    # ── Processing Settings ────────────────────────────────────────────────────
    MAX_IMAGE_SIZE: int = 4096
    DEFAULT_STEPS: int = 30
    DEFAULT_CFG_SCALE: float = 7.5
    MAX_BATCH_SIZE: int = 4
    
    # ── MCP Server ─────────────────────────────────────────────────────────────
    MCP_SERVER_ENABLED: bool = True
    MCP_SERVER_PORT: int = 7778
    MCP_TOOLS_PORT: int = 7779
    
    # ── Plugins ─────────────────────────────────────────────────────────────────
    PLUGINS_DIR: Path = WORKSPACE_DIR / "plugins"
    PLUGIN_CACHE_ENABLED: bool = True
    
    # ── Database ───────────────────────────────────────────────────────────────
    DATABASE_URL: str = f"sqlite+aiosqlite:///{WORKSPACE_DIR}/dolphinphoto.db"
    
    # ── Security ───────────────────────────────────────────────────────────────
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # ── CORS ───────────────────────────────────────────────────────────────────
    CORS_ORIGINS: list[str] = ["*"]
    
    # ── Performance ────────────────────────────────────────────────────────────
    ENABLE_WEBGPU: bool = False
    USE_XFORMERS: bool = False
    ENABLE_MEMORY_OPTIMIZATION: bool = True
    
    def update_workspace(self, workspace_dir: Path) -> None:
        """Update workspace directory paths."""
        self.WORKSPACE_DIR = workspace_dir
        self.MODELS_DIR = workspace_dir / "models"
        self.OUTPUTS_DIR = workspace_dir / "outputs"
        self.WORKFLOWS_DIR = workspace_dir / "workflows"
        self.TEMP_DIR = workspace_dir / "temp"
        self.PROJECTS_DIR = workspace_dir / "projects"
        self.CACHE_DIR = workspace_dir / "cache"
        self.PLUGINS_DIR = workspace_dir / "plugins"
        self.DATABASE_URL = f"sqlite+aiosqlite:///{workspace_dir}/dolphinphoto.db"
    
    def ensure_dirs(self) -> None:
        """Ensure all workspace directories exist."""
        for dir_path in [
            self.WORKSPACE_DIR,
            self.MODELS_DIR,
            self.OUTPUTS_DIR,
            self.WORKFLOWS_DIR,
            self.TEMP_DIR,
            self.PROJECTS_DIR,
            self.CACHE_DIR,
            self.PLUGINS_DIR,
        ]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    @property
    def models_path(self) -> Path:
        return self.MODELS_DIR
    
    @property
    def outputs_path(self) -> Path:
        return self.OUTPUTS_DIR
    
    @property
    def workflows_path(self) -> Path:
        return self.WORKFLOWS_DIR


_settings: Settings | None = None


def get_settings() -> Settings:
    """Get cached settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
        _settings.ensure_dirs()
    return _settings


def reload_settings() -> Settings:
    """Force reload settings."""
    global _settings
    _settings = Settings()
    _settings.ensure_dirs()
    return _settings
