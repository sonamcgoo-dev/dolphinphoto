"""
DolphinPhoto AI Studio - Main Entry Point
"""
from __future__ import annotations

from contextlib import asynccontextmanager

import uvicorn
from app.core.config import get_settings
from app.core.database import init_db
from app.mcp.server import mcp_server
from app.plugins.manager import plugin_manager
from app.services.device_service import device_service
from app.services.job_manager import job_manager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()
settings = get_settings()


def _print_banner() -> None:
    """Print application banner."""
    text = Text()
    text.append("🐬 DolphinPhoto", style="bold cyan")
    text.append(f" AI Studio v{settings.VERSION}", style="bold white")
    text.append(f"\n\n   {settings.DESCRIPTION}", style="dim white")
    text.append(f"\n   {settings.COMPANY}", style="dim")
    text.append(f"\n   Lead Dev: {settings.LEAD_DEV}", style="dim")
    text.append(f"\n\n   ─────────── Hardware ───────────", style="dim")
    text.append(f"\n   Device : ", style="white")
    text.append(settings.DEVICE.upper(), style="bold magenta")
    text.append(f" ({device_service.info.device_name})", style="dim")
    text.append(f"\n   RAM    : {device_service.info.ram_gb:.1f} GB", style="white")
    if device_service.info.vram_gb:
        text.append(f"\n   VRAM   : {device_service.info.vram_gb:.1f} GB", style="white")
    text.append(f"\n   Tier   : {device_service.info.performance_tier}", style="bold green")
    text.append(f"\n\n   ─────────── Services ───────────", style="dim")
    text.append(f"\n   API    : http://{settings.HOST}:{settings.PORT}/api/v1", style="bold cyan")
    text.append(f"\n   Docs   : http://{settings.HOST}:{settings.PORT}/api/docs", style="cyan")
    text.append(f"\n   MCP    : http://{settings.HOST}:{settings.MCP_SERVER_PORT}", style="cyan")
    
    console.print(Panel(
        text, 
        title="[bold cyan]🐬 DolphinPhoto AI Studio[/bold cyan]", 
        border_style="cyan",
        padding=(1, 2),
    ))


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # ── Startup ───────────────────────────────────────────────────────────────
    _print_banner()
    
    # Initialize database
    await init_db()
    console.print("[cyan]✓[/cyan] Database initialized")
    
    # Reset stale jobs
    await job_manager.reset_stale_jobs()
    console.print("[cyan]✓[/cyan] Job manager ready")
    
    # Load workspace settings
    from pathlib import Path
    from app.core.database import AsyncSessionLocal
    from app.models.db_models import Setting
    from sqlalchemy import select
    
    async with AsyncSessionLocal() as db:
        rows = await db.execute(select(Setting))
        cfg = {r.key: r.value for r in rows.scalars().all()}
    
    if cfg.get("workspace_dir"):
        settings.update_workspace(Path(cfg["workspace_dir"]))
        settings.ensure_dirs()
        console.print(f"[cyan]✓[/cyan] Workspace: {cfg['workspace_dir']}")
    
    if cfg.get("setup_complete") == "true":
        settings.SETUP_COMPLETE = True
    
    if cfg.get("civitai_api_key"):
        settings.CIVITAI_API_KEY = cfg["civitai_api_key"]
    
    # Load plugins
    plugin_manager.discover_and_load(settings.PLUGINS_DIR)
    console.print(f"[cyan]✓[/cyan] {len(plugin_manager.all())} plugins loaded")
    
    # MCP tools available
    tools = mcp_server.list_tools()
    console.print(f"[cyan]✓[/cyan] {len(tools)} MCP tools registered")
    
    console.print("\n[bold green]🚀 Server ready![/bold green]\n")
    
    yield
    
    # ── Shutdown ──────────────────────────────────────────────────────────────
    console.print("\n[cyan]Shutting down DolphinPhoto...[/cyan]")
    for plugin in plugin_manager.all():
        plugin.on_unload()
    console.print("[cyan]✓[/cyan] Cleanup complete")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# ── CORS Middleware ────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API Routers ─────────────────────────────────────────────────────────────────
from app.api.v1 import dream_video as dream_video_router
from app.api.v1 import filters as filters_router
from app.api.v1 import images, jobs, mcp as mcp_router
from app.api.v1 import models as models_router
from app.api.v1 import setup, video
from app.api.v1 import workspace as workspace_router

app.include_router(setup.router, prefix=settings.API_V1_STR)
app.include_router(images.router, prefix=settings.API_V1_STR)
app.include_router(video.router, prefix=settings.API_V1_STR)
app.include_router(filters_router.router, prefix=settings.API_V1_STR)
app.include_router(jobs.router, prefix=settings.API_V1_STR)
app.include_router(models_router.router, prefix=settings.API_V1_STR)
app.include_router(dream_video_router.router, prefix=settings.API_V1_STR)
app.include_router(mcp_router.router, prefix=settings.API_V1_STR)
app.include_router(workspace_router.router, prefix=settings.API_V1_STR)


# ── Root Endpoints ──────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.APP_NAME,
        "company": settings.COMPANY,
        "version": settings.VERSION,
        "description": settings.DESCRIPTION,
        "status": "running",
        "api": f"http://{settings.HOST}:{settings.PORT}{settings.API_V1_STR}",
        "docs": f"http://{settings.HOST}:{settings.PORT}/api/docs",
        "mcp": f"http://{settings.HOST}:{settings.MCP_SERVER_PORT}",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "version": settings.VERSION,
        "device": device_service.info.model_dump(),
        "setup_complete": settings.SETUP_COMPLETE,
        "plugins_loaded": len(plugin_manager.all()),
        "mcp_tools": len(mcp_server.list_tools()),
    }


@app.get("/status")
async def status():
    """Detailed status endpoint."""
    from app.core.database import AsyncSessionLocal
    from app.models.db_models import Job
    from sqlalchemy import select, func
    
    async with AsyncSessionLocal() as db:
        total_jobs = await db.execute(select(func.count(Job.id)))
        pending_jobs = await db.execute(
            select(func.count(Job.id)).where(Job.status == "pending")
        )
        running_jobs = await db.execute(
            select(func.count(Job.id)).where(Job.status == "running")
        )
    
    return {
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "running": True,
        "device": device_service.info.device,
        "performance_tier": device_service.info.performance_tier,
        "workspace": str(settings.WORKSPACE_DIR),
        "models_dir": str(settings.MODELS_DIR),
        "outputs_dir": str(settings.OUTPUTS_DIR),
        "jobs": {
            "total": total_jobs.scalar(),
            "pending": pending_jobs.scalar(),
            "running": running_jobs.scalar(),
        },
        "plugins": len(plugin_manager.all()),
        "mcp_tools": len(mcp_server.list_tools()),
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=False,
        log_level="warning",
    )
