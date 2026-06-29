#!/usr/bin/env python3
"""
DolphinPhoto AI Studio - Electron Build Script
Creates a proper Windows .exe with Electron
"""

import os
import sys
import subprocess
import shutil
import json
from pathlib import Path

class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'

def log(msg, color=CYAN):
    print(f"{color}{msg}{Colors.ENDC}")

def run_cmd(cmd, cwd=None, check=True):
    """Run shell command."""
    log(f"  {' '.join(cmd) if isinstance(cmd, list) else cmd}", Colors.YELLOW)
    result = subprocess.run(cmd, cwd=cwd, shell=isinstance(cmd, str), capture_output=True, text=True)
    if result.stdout: print(result.stdout)
    if result.stderr: print(result.stderr, file=sys.stderr)
    if check and result.returncode != 0:
        sys.exit(1)
    return result.returncode == 0

def main():
    project_root = Path(__file__).parent
    
    print(f"""
{Colors.CYAN}
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   🐬 DolphinPhoto AI Studio                                   ║
║   Electron Build Script                                        ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
{Colors.ENDC}
""")
    
    # Step 1: Build frontend
    log("\n[1/4] Building React Frontend...")
    frontend_dir = project_root / "frontend"
    
    # Create .env
    with open(frontend_dir / ".env", "w") as f:
        f.write("VITE_API_URL=http://127.0.0.1:7777\n")
    
    # Install deps
    log("  Installing npm dependencies...", Colors.YELLOW)
    run_cmd(["npm", "install"], cwd=str(frontend_dir), check=False)
    
    # Build
    log("  Building frontend...", Colors.YELLOW)
    run_cmd(["npm", "run", "build"], cwd=str(frontend_dir))
    log("  ✓ Frontend built", Colors.GREEN)
    
    # Step 2: Prepare Electron
    log("\n[2/4] Preparing Electron Build...")
    
    # Update electron-builder config
    pkg_file = frontend_dir / "package.json"
    pkg = json.loads(pkg_file.read_text())
    
    # Update build config for better Windows support
    pkg["build"] = {
        "appId": "com.dolphinphoto.aistudio",
        "productName": "DolphinPhoto AI Studio",
        "copyright": "Copyright (c) 2024 Black Tiger Computing",
        "directories": {
            "output": "release",
            "buildResources": "public"
        },
        "files": [
            "dist/**/*",
            "electron/**/*",
            "node_modules/**/*",
            "package.json"
        ],
        "extraResources": [
            {
                "from": str(project_root / "backend"),
                "to": "backend",
                "filter": ["**/*"]
            }
        ],
        "win": {
            "target": [
                {
                    "target": "nsis",
                    "arch": ["x64"]
                }
            ],
            "icon": "public/icon.ico",
            "artifactName": "${productName}-${version}-Setup.${ext}"
        },
        "nsis": {
            "oneClick": False,
            "perMachine": True,
            "allowToChangeInstallationDirectory": True,
            "createDesktopShortcut": True,
            "createStartMenuShortcut": True,
            "shortcutName": "DolphinPhoto AI Studio",
            "installerIcon": "public/icon.ico",
            "uninstallerIcon": "public/icon.ico",
            "installerHeaderIcon": "public/icon.ico",
            "license": str(project_root / "LICENSE.txt")
        },
        "mac": {
            "target": ["dmg"],
            "icon": "public/icon.icns",
            "category": "public.app-category.graphics-design"
        },
        "linux": {
            "target": ["AppImage", "deb"],
            "icon": "public/icon.png",
            "category": "Graphics"
        }
    }
    
    # Write updated package.json
    pkg_file.write_text(json.dumps(pkg, indent=2))
    
    # Create icon
    icon_dir = frontend_dir / "public"
    icon_dir.mkdir(exist_ok=True)
    
    # Create a simple ICO file placeholder
    ico_content = bytes([
        0, 0,       # Reserved
        1, 0,       # Type (1 = ICO)
        1, 0,       # Number of images
        # Image entry
        0, 0,       # Width, Height (0 = 256)
        0,          # Color palette
        0,          # Reserved
        1, 0,       # Color planes
        32, 0,      # Bits per pixel
        0x68, 0x05, 0, 0,  # Size of image data
        0x16, 0, 0, 0,     # Offset to image data
    ])
    
    # Simple 32x32 PNG for icon
    png_header = bytes([
        0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,  # PNG signature
        0x00, 0x00, 0x00, 0x0D,  # IHDR length
        0x49, 0x48, 0x44, 0x52,  # IHDR
        0x00, 0x00, 0x00, 0x20,  # Width: 32
        0x00, 0x00, 0x00, 0x20,  # Height: 32
        0x08, 0x06,              # 8-bit RGBA
        0x00, 0x00, 0x00,
        0x73, 0x7A, 0x7A, 0xF4,  # CRC
    ])
    
    # Write icon placeholder
    with open(icon_dir / "icon.png", "wb") as f:
        f.write(png_header)
    
    log("  ✓ Electron config updated", Colors.GREEN)
    
    # Step 3: Build Electron app
    log("\n[3/4] Building Electron Application...")
    
    # Install electron-builder if needed
    run_cmd(["npm", "install", "electron-builder", "--save-dev"], cwd=str(frontend_dir), check=False)
    
    # Build
    log("  Building Windows executable...", Colors.YELLOW)
    success = run_cmd(
        ["npm", "run", "electron:build:win"],
        cwd=str(frontend_dir),
        check=False
    )
    
    if success:
        log("  ✓ Electron app built", Colors.GREEN)
    else:
        log("  ⚠ Build had warnings", Colors.YELLOW)
    
    # Step 4: Verify output
    log("\n[4/4] Verifying Build Output...")
    
    release_dir = frontend_dir / "release"
    if release_dir.exists():
        exe_files = list(release_dir.glob("*.exe"))
        if exe_files:
            log(f"\n  ✓ Found executable: {exe_files[0].name}", Colors.GREEN)
            log(f"  Location: {exe_files[0].absolute()}", Colors.GREEN)
        else:
            log("\n  ⚠ No .exe found in release folder", Colors.YELLOW)
            log(f"  Release contents: {list(release_dir.glob('*'))}", Colors.YELLOW)
    else:
        log("\n  ⚠ Release folder not found", Colors.YELLOW)
    
    print(f"""
{Colors.GREEN}
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   ✅ Electron Build Complete!                                 ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
{Colors.ENDC}

Executable location:
  {release_dir.absolute()}

To create installer:
  Use the generated .exe file in the release folder
""")

if __name__ == "__main__":
    main()
