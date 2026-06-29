# DolphinPhoto AI Studio - Windows Executable Builder
# Creates a standalone Windows .exe with embedded Python

import os
import sys
import shutil
import subprocess
from pathlib import Path

def print_step(msg):
    print(f"\n{'='*60}")
    print(f"  {msg}")
    print(f"{'='*60}\n")

def run_cmd(cmd, cwd=None, check=True):
    """Run a command and return result."""
    print(f"Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    result = subprocess.run(
        cmd if isinstance(cmd, list) else cmd.split(),
        cwd=cwd,
        capture_output=True,
        text=True,
        shell=isinstance(cmd, str)
    )
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if check and result.returncode != 0:
        print(f"Command failed with exit code {result.returncode}")
        sys.exit(1)
    return result

def main():
    project_root = Path(__file__).parent.parent
    build_dir = project_root / "build"
    dist_dir = project_root / "dist"
    
    print_step("DolphinPhoto AI Studio - Windows Build")
    
    # Clean previous builds
    print("Cleaning previous builds...")
    if build_dir.exists():
        shutil.rmtree(build_dir)
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    
    build_dir.mkdir(exist_ok=True)
    
    # Step 1: Build Python backend with PyInstaller
    print_step("Step 1: Building Python Backend")
    
    backend_dir = project_root / "backend"
    
    # Create PyInstaller spec file
    spec_content = f"""
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['{backend_dir / "main.py"}'],
    pathex=['{backend_dir}'],
    binaries=[],
    datas=[
        ('{backend_dir}', 'app'),
    ],
    hiddenimports=[
        'uvicorn',
        'fastapi',
        'torch',
        'diffusers',
        'transformers',
        'PIL',
        'cv2',
        'numpy',
        'scipy',
        'skimage',
        'rembg',
        'onnxruntime',
        'realesrgan',
        'basicsr',
        'moviepy',
        'imageio',
        'sqlalchemy',
        'aiosqlite',
        'pydantic',
        'pydantic_settings',
        'httpx',
        'psutil',
        'rich',
        'loguru',
        'anyio',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='DolphinPhotoBackend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='DolphinPhotoBackend',
)

# Create main executable that starts backend
main_exe = EXE(
    pyz,
    a.scripts + [('start_backend.py', '''import subprocess, sys, os, time
os.chdir(os.path.dirname(sys.executable))
backend = subprocess.Popen([os.path.join(os.path.dirname(sys.executable), "DolphinPhotoBackend.exe")])
time.sleep(2)
sys.exit(0
''' , 'PYMODULE')],
    [],
    exclude_binaries=True,
    name='DolphinPhoto',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
)
"""
    
    with open(build_dir / "dolphinphoto.spec", "w") as f:
        f.write(spec_content)
    
    # Step 2: Build React frontend
    print_step("Step 2: Building React Frontend")
    
    frontend_dir = project_root / "frontend"
    
    # Create environment file
    with open(frontend_dir / ".env", "w") as f:
        f.write("VITE_API_URL=http://127.0.0.1:7777\n")
    
    # Build frontend
    run_cmd(["npm", "install"], cwd=frontend_dir)
    run_cmd(["npm", "run", "build"], cwd=frontend_dir)
    
    # Step 3: Package everything together
    print_step("Step 3: Packaging Everything")
    
    # Copy backend build
    backend_dist = dist_dir / "backend"
    backend_dist.mkdir(exist_ok=True)
    
    # Copy frontend dist
    frontend_dist = dist_dir / "frontend"
    if (frontend_dir / "dist").exists():
        shutil.copytree(frontend_dir / "dist", frontend_dist)
    
    # Create startup script
    start_script = """@echo off
title DolphinPhoto AI Studio
color 0A

echo.
echo    ============================================================
echo.
echo       DolphinPhoto AI Studio
echo       The Ultimate AI Creative Studio
echo.
echo    ============================================================
echo.

REM Start Backend
echo [1/2] Starting Backend Server...
start "DolphinPhoto Backend" cmd /k "cd /d %~dp0backend && DolphinPhotoBackend.exe"

REM Wait for backend
timeout /t 3 /nobreak >nul

REM Start Frontend
echo [2/2] Starting Frontend...
cd frontend
start "" "http://localhost:5173"
cd ..

echo.
echo    DolphinPhoto is running!
echo.
echo    Frontend: http://localhost:5173
echo    Backend:  http://127.0.0.1:7777
echo.
echo    Press any key to exit...
pause >nul
"""
    
    with open(dist_dir / "DolphinPhoto.bat", "w") as f:
        f.write(start_script)
    
    # Create desktop shortcut script
    shortcut_script = """[Desktop Entry]
Name=DolphinPhoto AI Studio
Comment=The Ultimate AI Creative Studio
Exec={path}/DolphinPhoto.sh
Icon={path}/icon.png
Terminal=false
Type=Application
Categories=Graphics;Photo;Video;
"""
    
    # Create main shell script for Linux
    shell_script = """#!/bin/bash

echo "
============================================================

   DolphinPhoto AI Studio
   The Ultimate AI Creative Studio

============================================================
"

# Start backend
echo "[1/2] Starting Backend Server..."
cd backend
./DolphinPhotoBackend &
BACKEND_PID=$!
cd ..

sleep 3

# Open browser
echo "[2/2] Opening browser..."
xdg-open http://localhost:5173 2>/dev/null || open http://localhost:5173 2>/dev/null || echo "Open http://localhost:5173 manually"

echo "
DolphinPhoto is running!

Frontend: http://localhost:5173
Backend:  http://127.0.0.1:7777

Press Ctrl+C to stop...
"

# Wait for Ctrl+C
trap "kill $BACKEND_PID 2>/dev/null; exit" SIGINT SIGTERM
wait
"""
    
    with open(dist_dir / "DolphinPhoto.sh", "w") as f:
        f.write(shell_script)
    
    # Step 4: Create README for distribution
    print_step("Step 4: Creating Distribution Package")
    
    readme = """
# DolphinPhoto AI Studio - Distribution Package

## Quick Start

### Windows
1. Double-click `DolphinPhoto.bat` to start
2. The app will open in your browser at http://localhost:5173

### Linux
1. Make the script executable: `chmod +x DolphinPhoto.sh`
2. Run: `./DolphinPhoto.sh`

### macOS
1. Make the script executable: `chmod +x DolphinPhoto.sh`
2. Run: `./DolphinPhoto.sh`

## Features

- AI Image Generation (Stable Diffusion)
- Dream Video Creation
- AI Photo Glowup
- 60+ Filters (Social, Artistic, Color, Glitch, Vintage)
- Model Management (CivitAI, HuggingFace)
- MCP Tool Integration
- Full Desktop Integration

## Requirements

- Windows 10/11, Linux, or macOS
- 8GB RAM minimum (16GB recommended)
- For GPU acceleration: NVIDIA GPU with 4GB+ VRAM

## Troubleshooting

### Backend won't start
- Check if port 7777 is available
- Try running DolphinPhoto.bat as administrator

### Frontend won't load
- Make sure backend started successfully
- Try refreshing the browser

### Slow performance
- GPU acceleration requires CUDA-compatible NVIDIA GPU
- Close other resource-intensive applications

## Support

For issues and feedback:
- GitHub: https://github.com/dolphinphoto/issues
- Email: support@dolphinphoto.ai

---

Built with ❤️ by Black Tiger Computing
Lead Developer: Sona McGoo
"""
    
    with open(dist_dir / "README.txt", "w") as f:
        f.write(readme)
    
    print_step("Build Complete!")
    print(f"""
    Distribution package created at: {dist_dir}
    
    To create the .exe installer:
    1. Install NSIS (https://nsis.sourceforge.io/)
    2. Use the installer script in build/
    
    Or distribute the 'dist' folder directly.
    """)

if __name__ == "__main__":
    main()
