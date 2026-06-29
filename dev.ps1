# ── DolphinPhoto dev launcher (PowerShell) ────────────────────────────────────
# Run from PowerShell:  .\dev.ps1
# Does NOT work from Git Bash — use PowerShell or Windows Terminal.

$NODE_DIR = "C:\Users\RANCORE\node\node-v22.16.0-win-x64"
$env:PATH  = "$NODE_DIR;$env:PATH"
$env:TEMP  = "C:\Users\RANCORE\AppData\Local\Temp"
$env:TMP   = "C:\Users\RANCORE\AppData\Local\Temp"

# ── Backend ───────────────────────────────────────────────────────────────────
Write-Host "[DolphinPhoto] Starting FastAPI backend..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", `
  "cd '$PSScriptRoot\backend'; python main.py"

# ── Frontend (Vite dev server) ────────────────────────────────────────────────
Write-Host "[DolphinPhoto] Starting Vite dev server on http://localhost:5173" -ForegroundColor Cyan
Set-Location "$PSScriptRoot\frontend"
& "node_modules\.bin\vite.cmd"
