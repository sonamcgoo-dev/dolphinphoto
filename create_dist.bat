@echo off
chcp 65001 >nul
title DolphinPhoto AI Studio - Build

echo.
echo  ============================================================
echo.
echo     DolphinPhoto AI Studio
echo     Windows Build Script
echo.
echo  ============================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python 3.10+
    pause
    exit /b 1
)

REM Check Node
node --version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Node.js not found. Frontend build will be skipped.
    set NODE_SKIP=1
)

echo.
echo [1/5] Installing Python dependencies...
pip install -r backend\requirements.txt -q
if errorlevel 1 (
    echo [WARNING] Some Python packages may not have installed correctly
)

if not defined NODE_SKIP (
    echo.
    echo [2/5] Installing Node.js dependencies...
    cd frontend
    call npm install
    cd ..
    
    echo.
    echo [3/5] Building frontend...
    cd frontend
    call npm run build
    cd ..
) else (
    echo.
    echo [3/5] Skipping frontend build (Node.js not found)
)

echo.
echo [4/5] Creating distribution package...
mkdir dist\DolphinPhoto 2>nul

REM Copy backend
if exist "backend\main.py" (
    copy /E /Y "backend" "dist\DolphinPhoto\backend" >nul
)

REM Copy frontend dist if exists
if exist "frontend\dist" (
    copy /E /Y "frontend\dist" "dist\DolphinPhoto\frontend" >nul
)

REM Create startup script
(
echo @echo off
echo title DolphinPhoto AI Studio
echo color 0A
echo.
echo echo.
echo echo   ============================================================
echo echo.
echo echo      DolphinPhoto AI Studio
echo echo      The Ultimate AI Creative Studio
echo echo.
echo echo   ============================================================
echo echo.
echo.
echo REM Start Backend
echo echo [1] Starting Backend Server...
echo start "DolphinPhoto Backend" cmd /k "cd /d "%~dp0" ^&^& cd backend ^&^& python main.py"
echo.
echo REM Wait for backend
echo timeout /t 5 /nobreak >nul
echo.
echo REM Open browser
echo echo [2] Opening application...
echo start "" "http://localhost:5173"
echo.
echo echo.
echo echo   DolphinPhoto is running!
echo echo.
echo echo   Frontend: http://localhost:5173
echo echo   Backend:  http://127.0.0.1:7777
echo echo.
echo pause
) > "dist\DolphinPhoto\Run DolphinPhoto.bat"

REM Create standalone executable using PyInstaller
echo.
echo [5/5] Building standalone executable...

REM Install pyinstaller
pip install pyinstaller -q

REM Build backend executable
cd backend
python -m PyInstaller --onefile --name DolphinPhotoBackend --console --add-data "app;app" main.py --noconfirm --clean >nul 2>&1
cd ..

REM Copy backend exe
if exist "backend\dist\DolphinPhotoBackend.exe" (
    copy "backend\dist\DolphinPhotoBackend.exe" "dist\DolphinPhoto\DolphinPhotoBackend.exe" >nul
)

echo.
echo  ============================================================
echo.
echo     Build Complete!
echo.
echo  ============================================================
echo.
echo  Distribution folder: dist\DolphinPhoto
echo.
echo  To run DolphinPhoto:
echo    - Double-click: "Run DolphinPhoto.bat"
echo    - Or: cd dist\DolphinPhoto ^&^& dolphinphoto.bat
echo.
echo  For a proper installer, run NSIS with:
echo    build\installer.nsi
echo.
pause
