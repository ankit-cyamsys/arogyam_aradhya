# Arogyam Aradhya — start both servers (Windows PowerShell)
# Usage:  right-click > Run with PowerShell, or:  ./start.ps1
$ErrorActionPreference = "Stop"
$root = $PSScriptRoot

Write-Host "Starting backend (FastAPI) on http://127.0.0.1:8000 ..." -ForegroundColor Green
Start-Process -FilePath "$root\backend\.venv\Scripts\python.exe" `
  -ArgumentList "-m", "uvicorn", "app.main:app", "--reload", "--port", "8000" `
  -WorkingDirectory "$root\backend"

Start-Sleep -Seconds 2

Write-Host "Starting frontend (Vite) on http://localhost:5173 ..." -ForegroundColor Green
Start-Process -FilePath "npm" -ArgumentList "run", "dev" -WorkingDirectory "$root\frontend"

Start-Sleep -Seconds 3
Write-Host ""
Write-Host "======================================================" -ForegroundColor Yellow
Write-Host "  Storefront : http://localhost:5173" -ForegroundColor Yellow
Write-Host "  API docs   : http://127.0.0.1:8000/docs" -ForegroundColor Yellow
Write-Host "  Admin      : http://localhost:5173/admin/login  (admin / admin123)" -ForegroundColor Yellow
Write-Host "======================================================" -ForegroundColor Yellow
Start-Process "http://localhost:5173"
