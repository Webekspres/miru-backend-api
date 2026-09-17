# MIRU Backend - jalankan native di Windows (tanpa Docker/WSL)
# Pakai: buka PowerShell di folder backend, jalankan:  .\scripts\run_win.ps1
param(
    [string]$BindHost = "0.0.0.0",
    [int]$Port = 8000
)

$ErrorActionPreference = "Stop"
$backendDir = Split-Path -Parent $PSScriptRoot
Set-Location $backendDir

# 1. Bersihkan proses lama yang masih memegang port (cegah "tiba-tiba disconnect")
$stale = (netstat -ano | Select-String ":$Port\s.*LISTENING") -replace '.*\s(\d+)$', '$1' | Sort-Object -Unique
foreach ($procId in $stale) {
    if ($procId) {
        Write-Host "Menutup proses lama di port $Port (PID $procId)..."
        Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
    }
}
Start-Sleep -Seconds 1

# 2. Jalankan server. --noreload + PYTHONUNBUFFERED lebih stabil di Windows/Python 3.14.
$env:PYTHONUNBUFFERED = "1"
& "$backendDir\venv\Scripts\python.exe" manage.py runserver "${BindHost}:${Port}" --noreload
