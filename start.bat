@echo off
chcp 65001 >nul

echo.
echo    ╔═══════════════════════════════════════════════════════════════╗
echo    ║                                                               ║
echo    ║   🐬 DolphinPhoto AI Studio                                    ║
echo    ║   The Ultimate AI Creative Studio                             ║
echo    ║                                                               ║
echo    ╚═══════════════════════════════════════════════════════════════╝
echo.

echo [1/4] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found! Please install Python 3.12+
    exit /b 1
)
echo   Python OK

echo [2/4] Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo Node.js not found! Please install Node.js 22+
    exit /b 1
)
echo   Node.js OK

echo [3/4] Installing Backend Dependencies...
pip install -r backend/requirements.txt -q
echo   Backend dependencies ready

echo [4/4] Installing Frontend Dependencies...
if not exist "frontend\node_modules" (
    cd frontend
    call npm install
    cd ..
    echo   Frontend dependencies ready
) else (
    echo   Node modules already installed
)

echo.
echo    ════════════════════════════════════════════════════════════════
echo.
echo    Starting services...
echo.
echo    Frontend:  http://localhost:5173
echo    Backend:   http://127.0.0.1:7777
echo    API Docs:  http://127.0.0.1:7777/api/docs
echo.
echo    Press Ctrl+C to stop all services
echo    ════════════════════════════════════════════════════════════════
echo.

start "DolphinPhoto Backend" cmd /k "cd /d %CD%\backend && python main.py"
timeout /t 3 /nobreak >nul
start "DolphinPhoto Frontend" cmd /k "cd /d %CD%\frontend && npm run dev"
