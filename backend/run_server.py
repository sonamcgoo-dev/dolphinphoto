#!/usr/bin/env python3
"""
DolphinPhoto AI Studio - Standalone Server Launcher
This script can be compiled with PyInstaller to create a standalone .exe
"""

import sys
import os
import subprocess
import time
import webbrowser
import threading
from pathlib import Path

# Set working directory to script location
SCRIPT_DIR = Path(__file__).parent
os.chdir(SCRIPT_DIR)

def print_banner():
    """Print startup banner."""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   🐬 DolphinPhoto AI Studio                                   ║
║   The Ultimate AI Creative Studio                             ║
║                                                               ║
║   Black Tiger Computing                                       ║
║   Lead Developer: Sona McGoo                                  ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
""")

def check_dependencies():
    """Check if required dependencies are installed."""
    missing = []
    
    # Check Python packages
    required_packages = [
        'fastapi', 'uvicorn', 'torch', 'diffusers',
        'PIL', 'cv2', 'numpy'
    ]
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    return missing

def start_backend():
    """Start the backend server."""
    print("[1/3] Starting Backend Server...")
    print("       URL: http://127.0.0.1:7777")
    print("       Docs: http://127.0.0.1:7777/api/docs")
    print()
    
    backend_process = subprocess.Popen(
        [sys.executable, "main.py"],
        cwd=str(SCRIPT_DIR),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    return backend_process

def start_frontend_server():
    """Start a simple frontend server if dist exists."""
    print("[2/3] Checking Frontend...")
    
    dist_dir = SCRIPT_DIR.parent / "frontend" / "dist"
    if dist_dir.exists():
        print(f"       Frontend build found at: {dist_dir}")
        return None
    
    print("       Frontend not found - using default URL")
    return None

def open_browser():
    """Open browser after delay."""
    time.sleep(3)
    print("[3/3] Opening Browser...")
    webbrowser.open("http://localhost:5173")

def main():
    """Main entry point."""
    print_banner()
    
    # Check dependencies
    print("Checking dependencies...")
    missing = check_dependencies()
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("   Install with: pip install -r requirements.txt")
        print()
    
    # Start backend
    backend_process = start_backend()
    
    # Open browser in background thread
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()
    
    print("DolphinPhoto AI Studio is running!")
    print()
    print("=" * 62)
    print()
    print("   Frontend:  http://localhost:5173")
    print("   Backend:   http://127.0.0.1:7777")
    print("   API Docs:  http://127.0.0.1:7777/api/docs")
    print()
    print("   Press Ctrl+C to stop the server")
    print()
    print("=" * 62)
    print()
    
    try:
        # Wait for backend process
        backend_process.wait()
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        backend_process.terminate()
        backend_process.wait()
        print("DolphinPhoto stopped.")

if __name__ == "__main__":
    main()
