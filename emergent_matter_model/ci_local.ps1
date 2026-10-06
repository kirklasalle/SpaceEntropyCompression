# Local CI equivalent for environments without GitHub Actions
# Runs Python unit tests, headless physics consistency check, and JavaFX Maven compile.

$ErrorActionPreference = 'Stop'

Push-Location $PSScriptRoot
try {
    Write-Host "[1/3] Python tests & physics check" -ForegroundColor Cyan
    $python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
    if (-not (Test-Path $python)) {
        throw "Canonical Python environment not found at $python. Create .venv first."
    }
    & $python -m pytest -v
    & $python compare_schwarzschild.py --headless

Write-Host "[2/3] Ensure Maven available" -ForegroundColor Cyan
$installMaven = Join-Path $PSScriptRoot "..\docs\install_maven.ps1"
if (Test-Path $installMaven) {
    & $installMaven
}

Write-Host "[3/3] JavaFX compile" -ForegroundColor Cyan
if (-not $env:JAVA_HOME -or -not (Test-Path $env:JAVA_HOME)) {
    if (Test-Path 'G:\Program Files\Java\jdk-25.0.2') {
        $env:JAVA_HOME = 'G:\Program Files\Java\jdk-25.0.2'
    } elseif (Test-Path 'C:\Program Files\Java\jdk-25.0.2') {
        $env:JAVA_HOME = 'C:\Program Files\Java\jdk-25.0.2'
    }
}
if ($env:JAVA_HOME -and (Test-Path $env:JAVA_HOME)) {
    $env:Path = "$env:JAVA_HOME\bin;" + $env:Path
}

$javafxDir = Join-Path $PSScriptRoot "javafx_client"
if (Test-Path $javafxDir) {
    Push-Location $javafxDir
    try {
        mvn -DskipTests compile
    } finally {
        Pop-Location
    }
}

    Write-Host "Local CI checks passed successfully." -ForegroundColor Green
} finally {
    Pop-Location
}
