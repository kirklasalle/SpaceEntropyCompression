# run_all.ps1 — unified setup, server, and test script
# Works from any machine (no hard-coded paths).
#
# Usage:
#   .\run_all.ps1              — full flow: venv, install, server, viz
#   .\run_all.ps1 -SkipServer  — skip starting the server (already running)

param(
    [switch]$SkipServer
)

$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot   # always run relative to this script

# 1. Virtual environment
if (-not (Test-Path ".\.venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv .venv
}
. .\.venv\Scripts\Activate

# 2. Install / upgrade dependencies
python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt --quiet

# 3. Run unit tests first
Write-Host "`n=== Running tests ==="
python -m pytest test_model.py -v
if ($LASTEXITCODE -ne 0) {
    Write-Host "Tests failed — aborting." -ForegroundColor Red
    exit 1
}

# 4. Start server (unless skipped)
if (-not $SkipServer) {
    Write-Host "`n=== Starting server ==="
    $serverJob = Start-Process -NoNewWindow -PassThru -FilePath python -ArgumentList "server.py"
    Start-Sleep -Seconds 4
}

# 5. Run the 2D visualisation client
Write-Host "`n=== 2D Visualisation ==="
python visualize.py

# 6. (Optional) Run JavaFX client if Maven is available
$pomPath = Join-Path $PSScriptRoot "javafx_client\pom.xml"
if ((Test-Path $pomPath) -and (Get-Command mvn -ErrorAction SilentlyContinue)) {
    Write-Host "`n=== JavaFX Client ==="
    Push-Location javafx_client
    mvn clean javafx:run
    Pop-Location
}

# 7. Clean up server
if (-not $SkipServer -and $serverJob) {
    Stop-Process -Id $serverJob.Id -ErrorAction SilentlyContinue
    Write-Host "Server stopped."
}

Write-Host "`nDone." -ForegroundColor Green
