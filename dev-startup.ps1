# Fantasy Football Analysis - Development Startup Script
# Starts both backend API and frontend dev server in separate terminals

# Get the script directory
$scriptDir = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition

# Start Backend in new terminal
Write-Host "Starting backend API server..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptDir'; .\.venv\Scripts\Activate.ps1; python run_api.py" -WindowStyle Normal

# Wait a moment for backend to start
Start-Sleep -Seconds 2

# Start Frontend in new terminal (using cmd.exe to avoid PowerShell execution policy)
Write-Host "Starting frontend dev server..." -ForegroundColor Green
$frontendPath = Join-Path $scriptDir "frontend"
Start-Process cmd.exe -ArgumentList "/k", "cd /d `"$frontendPath`" && npm run dev" -WindowStyle Normal

Write-Host "`nBoth servers are starting:`n" -ForegroundColor Cyan
Write-Host "  Backend API: http://localhost:8000" -ForegroundColor Yellow
Write-Host "  Frontend:    http://localhost:3000" -ForegroundColor Yellow
