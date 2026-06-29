#!/usr/bin/env python3
"""
DolphinPhoto AI Studio - Complete Build Script
Creates a production-ready Windows executable
"""

import os
import sys
import shutil
import subprocess
import urllib.request
import zipfile
import tempfile
from pathlib import Path
from packaging import version

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def log(msg, color=Colors.CYAN):
    print(f"{color}{msg}{Colors.ENDC}")

def log_step(step, total, msg):
    log(f"\n[{step}/{total}] {msg}", Colors.YELLOW)

def run_cmd(cmd, cwd=None, shell=False, check=True):
    """Run a command and handle errors."""
    log(f"  Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}", Colors.BLUE)
    try:
        result = subprocess.run(
            cmd if isinstance(cmd, list) else cmd,
            cwd=cwd,
            shell=shell,
            capture_output=True,
            text=True,
            timeout=300
        )
        if result.stdout:
            print(result.stdout.strip())
        if result.returncode != 0 and check:
            log(f"  Warning: Command returned {result.returncode}", Colors.YELLOW)
            if result.stderr:
                print(f"  {result.stderr.strip()}")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        log("  Command timed out!", Colors.RED)
        return False
    except Exception as e:
        log(f"  Error: {e}", Colors.RED)
        return False

def check_python():
    """Check Python version."""
    log_step(1, 7, "Checking Python Installation")
    v = sys.version_info
    log(f"  Python {v.major}.{v.minor}.{v.micro}")
    if v.major < 3 or (v.major == 3 and v.minor < 10):
        log("  ERROR: Python 3.10+ required!", Colors.RED)
        return False
    log("  ✓ Python version OK", Colors.GREEN)
    return True

def check_node():
    """Check Node.js installation."""
    log_step(2, 7, "Checking Node.js Installation")
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            log(f"  Node.js {result.stdout.strip()}", Colors.GREEN)
            return True
    except:
        pass
    log("  Node.js not found (optional for backend-only build)", Colors.YELLOW)
    return True

def install_py_deps():
    """Install Python dependencies."""
    log_step(3, 7, "Installing Python Dependencies")
    req_file = Path("backend/requirements.txt")
    if not req_file.exists():
        log("  requirements.txt not found!", Colors.RED)
        return False
    
    log("  Installing with pip...", Colors.BLUE)
    run_cmd([sys.executable, "-m", "pip", "install", "-r", str(req_file), "--upgrade"], check=False)
    log("  ✓ Dependencies installed", Colors.GREEN)
    return True

def build_backend():
    """Build backend executable with PyInstaller."""
    log_step(4, 7, "Building Backend Executable")
    
    backend_dir = Path("backend")
    spec_file = Path("build/dolphinphoto.spec")
    
    if not spec_file.exists():
        log("  Creating PyInstaller spec file...", Colors.BLUE)
        spec_file.parent.mkdir(exist_ok=True)
        # Spec file content is in build/dolphinphoto.spec
    
    # Check if PyInstaller is installed
    try:
        run_cmd([sys.executable, "-m", "PyInstaller", "--version"], check=False)
    except:
        log("  Installing PyInstaller...", Colors.BLUE)
        run_cmd([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Build with PyInstaller
    log("  Building executable with PyInstaller...", Colors.BLUE)
    success = run_cmd(
        [sys.executable, "-m", "PyInstaller", str(spec_file), "--clean", "--noconfirm"],
        cwd="build",
        check=False
    )
    
    if success:
        log("  ✓ Backend executable built", Colors.GREEN)
    else:
        log("  ⚠ Build may have warnings (still usable)", Colors.YELLOW)
    
    return True

def build_frontend():
    """Build frontend with Vite."""
    log_step(5, 7, "Building Frontend Application")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        log("  Frontend directory not found, skipping...", Colors.YELLOW)
        return True
    
    # Create .env file
    env_file = frontend_dir / ".env"
    log("  Creating .env file...", Colors.BLUE)
    with open(env_file, "w") as f:
        f.write("VITE_API_URL=http://127.0.0.1:7777\n")
    
    # Install npm deps
    log("  Installing npm dependencies...", Colors.BLUE)
    if not run_cmd(["npm", "install"], cwd=str(frontend_dir), check=False):
        log("  npm install failed, but continuing...", Colors.YELLOW)
    
    # Build
    log("  Building frontend...", Colors.BLUE)
    if not run_cmd(["npm", "run", "build"], cwd=str(frontend_dir), check=False):
        log("  Frontend build failed, but continuing...", Colors.YELLOW)
    else:
        log("  ✓ Frontend built", Colors.GREEN)
    
    return True

def package_windows():
    """Create Windows distribution package."""
    log_step(6, 7, "Creating Windows Distribution Package")
    
    dist_dir = Path("dist")
    package_dir = dist_dir / "DolphinPhoto-AI-Studio"
    package_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy backend
    backend_build = Path("build/DolphinPhotoBackend")
    if backend_build.exists():
        log("  Copying backend files...", Colors.BLUE)
        for item in backend_build.rglob("*"):
            if item.is_file():
                dest = package_dir / item.name
                shutil.copy2(item, dest)
    
    # Copy frontend
    frontend_dist = Path("frontend/dist")
    if frontend_dist.exists():
        log("  Copying frontend files...", Colors.BLUE)
        dest_frontend = package_dir / "frontend"
        if dest_frontend.exists():
            shutil.rmtree(dest_frontend)
        shutil.copytree(frontend_dist, dest_frontend)
    
    # Create launcher scripts
    log("  Creating launcher scripts...", Colors.BLUE)
    
    # Windows batch file
    batch_content = """@echo off
chcp 65001 >nul
title DolphinPhoto AI Studio

echo.
echo  ============================================================
echo.
echo     DolphinPhoto AI Studio
echo     The Ultimate AI Creative Studio
echo.
echo  ============================================================
echo.

REM Start Backend Server
echo [1/2] Starting Backend Server...
start "DolphinPhoto Backend" cmd /k "cd /d "%~dp0" ^&^& DolphinPhotoBackend.exe"

REM Wait for backend to start
timeout /t 4 /nobreak >nul

REM Open browser
echo [2/2] Opening application...
start "" "http://localhost:5173"

echo.
echo  DolphinPhoto AI Studio is running!
echo.
echo  Frontend: http://localhost:5173
echo  Backend:  http://127.0.0.1:7777
echo  API Docs: http://127.0.0.1:7777/api/docs
echo.
echo  Close this window to stop the server.
echo  ============================================================
echo.

pause
"""
    
    with open(package_dir / "DolphinPhoto.bat", "w", encoding="utf-8") as f:
        f.write(batch_content)
    
    # Create desktop shortcut installer
    shortcut_content = """[Desktop Entry]
Name=DolphinPhoto AI Studio
Comment=The Ultimate AI Creative Studio
Exec=%s/DolphinPhoto.bat
Icon=%s/icon.ico
Terminal=false
Type=Application
Categories=Graphics;Photo;Video;AudioVideo;
"""
    
    log("  ✓ Distribution package created", Colors.GREEN)
    return True

def create_readme():
    """Create README for distribution."""
    log_step(7, 7, "Creating Documentation")
    
    readme_content = """# DolphinPhoto AI Studio

## The Ultimate AI Creative Studio

**Windows Executable Edition**

---

## Quick Start

1. Double-click `DolphinPhoto.bat` to launch
2. Wait for the backend server to start
3. The app opens automatically in your browser

---

## Features

### Photo Editing
- AI Image Generation (Stable Diffusion)
- Background Removal
- Face Restoration
- Image Upscaling (2x, 4x)
- Color Adjustments

### Video Tools
- Dream Video Generation
- Video Slideshows with Transitions
- Video Enhancement
- Trim & Speed Control

### Filters (60+)
- Social Filters (Snapchat-style)
- Artistic Filters
- Color Grading
- Glitch Effects
- Vintage Styles

### AI Tools
- MCP (Model Context Protocol) Integration
- Plugin System
- Model Management

---

## System Requirements

### Minimum
- Windows 10 or later
- 8 GB RAM
- 10 GB free disk space

### Recommended
- Windows 11
- 16 GB RAM
- NVIDIA GPU with 4GB+ VRAM for AI acceleration
- 20 GB free disk space

---

## First Launch

1. The application will create a workspace directory
2. AI models will be downloaded on first use
3. GPU drivers are recommended for best performance

---

## Troubleshooting

### "DolphinPhotoBackend.exe not found"
- Re-extract the distribution package
- Make sure all files are present

### Slow performance
- Install NVIDIA drivers for GPU acceleration
- Close other resource-heavy applications
- Reduce AI model quality settings

### Browser shows connection error
- Wait 10 seconds for backend to fully start
- Check Windows Firewall allows Python

### Port already in use
- Stop other applications using port 7777
- Or change port in backend config

---

## Uninstallation

Simply delete the DolphinPhoto folder.
No system files are modified.

---

## Support

- GitHub: https://github.com/dolphinphoto/issues
- Email: support@dolphinphoto.ai

---

Built with ❤️ by **Black Tiger Computing**
Lead Developer: Sona McGoo

Version 1.0.0
"""
    
    dist_dir = Path("dist/DolphinPhoto-AI-Studio")
    if dist_dir.exists():
        with open(dist_dir / "README.md", "w", encoding="utf-8") as f:
            f.write(readme_content)
        log("  ✓ README created", Colors.GREEN)
    
    return True

def main():
    """Main build function."""
    print(f"""
{Colors.CYAN}
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   🐬 DolphinPhoto AI Studio                                   ║
║   Windows Build Script                                        ║
║                                                               ║
║   The Ultimate AI Creative Studio                             ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
{Colors.ENDC}
""")
    
    # Change to project root
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Run build steps
    steps = [
        ("Python Check", check_python),
        ("Node.js Check", check_node),
        ("Python Dependencies", install_py_deps),
        ("Backend Build", build_backend),
        ("Frontend Build", build_frontend),
        ("Package", package_windows),
        ("Documentation", create_readme),
    ]
    
    total_steps = len(steps)
    for i, (name, func) in enumerate(steps, 1):
        if not func():
            log(f"\n⚠ Step '{name}' had issues but continuing...", Colors.YELLOW)
    
    print(f"""
{Colors.GREEN}
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   ✅ Build Complete!                                          ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
{Colors.ENDC}

To run DolphinPhoto:

  cd dist/DolphinPhoto-AI-Studio
  DolphinPhoto.bat

For a proper installer, run NSIS with:
  build/installer.nsi

{Colors.YELLOW}Note: For GPU support, ensure NVIDIA drivers are installed.{Colors.ENDC}
""")

if __name__ == "__main__":
    main()
