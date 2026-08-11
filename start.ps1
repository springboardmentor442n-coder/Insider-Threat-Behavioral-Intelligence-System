# ============================================================
# Insider Threat Behavioral Intelligence System
# One-Command Development Launcher
# ============================================================

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$FrontendPath = Join-Path $ProjectRoot "insider-threat-frontend"

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host " Insider Threat Behavioral Intelligence" -ForegroundColor Cyan
Write-Host " Development Environment" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# ------------------------------------------------------------
# Check Backend Port
# ------------------------------------------------------------

$backendPort = Get-NetTCPConnection `
    -LocalPort 8000 `
    -State Listen `
    -ErrorAction SilentlyContinue

if ($backendPort) {

    Write-Host "Backend already running on port 8000." -ForegroundColor Green

}
else {

    Write-Host "Starting FastAPI backend..." -ForegroundColor Yellow

    Start-Job -ScriptBlock {
        param($Root)

        Set-Location $Root

        python -m uvicorn `
            backend.app:app `
            --reload `
            --host 127.0.0.1 `
            --port 8000

    } -ArgumentList $ProjectRoot | Out-Null

}

# ------------------------------------------------------------
# Start Frontend
# ------------------------------------------------------------

Write-Host "Starting React frontend..." -ForegroundColor Yellow

Set-Location $FrontendPath

npm run dev

# ------------------------------------------------------------
# End
# ------------------------------------------------------------