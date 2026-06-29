# Build Instructions for DolphinPhoto AI Studio

## Quick Build (Windows)

### Option 1: Use the Build Script
```batch
create_dist.bat
```

### Option 2: Manual Build

1. **Install Python dependencies:**
```bash
cd backend
pip install -r requirements.txt
```

2. **Build Frontend:**
```bash
cd frontend
npm install
npm run build
```

3. **Create Distribution:**
```bash
# Run the create_dist.bat script
create_dist.bat
```

## PyInstaller (Standalone EXE)

### Install PyInstaller
```bash
pip install pyinstaller
```

### Build Backend EXE
```bash
cd backend
pyinstaller --onefile --name DolphinPhotoBackend --console --add-data "app;app" main.py
```

### Create Full Distribution
The `dist/` folder will contain:
- `DolphinPhotoBackend.exe` - Backend server
- `Run DolphinPhoto.bat` - Launcher script
- `backend/` - Python source
- `frontend/` - Web interface

## Electron (Full Desktop App)

### Install Electron Builder
```bash
cd frontend
npm install electron-builder --save-dev
```

### Build Windows EXE
```bash
npm run electron:build:win
```

Output: `frontend/release/DolphinPhoto AI Studio-1.0.0-Setup.exe`

## NSIS Installer

### Install NSIS
Download from: https://nsis.sourceforge.io/

### Create Installer
```batch
cd build
makensis installer.nsi
```

Output: `build/DolphinPhoto-Setup.exe`

## Build with Python Script

```bash
python build_launcher.py
```

This will:
1. Check Python installation
2. Install dependencies
3. Build backend with PyInstaller
4. Build frontend with Vite
5. Create distribution package

## Requirements

- Windows 10/11, macOS, or Linux
- Python 3.10+
- Node.js 18+ (for frontend)
- 8GB RAM minimum
- 10GB disk space

## Post-Build

After building, you can distribute:
- The `dist/DolphinPhoto` folder
- Or the installer from `build/`
