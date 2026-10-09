# Local CI equivalent for environments without GitHub Actions.
# Runs the same Python safety checks, headless physics check, and JavaFX compile.

$ErrorActionPreference = 'Stop'

function Assert-LastExitCode([string]$Step) {
    if ($LASTEXITCODE -ne 0) {
        throw "$Step failed with exit code $LASTEXITCODE."
    }
}

Push-Location $PSScriptRoot
try {
    Write-Host "[1/4] Python safety checks" -ForegroundColor Cyan
    $python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
    if (-not (Test-Path $python)) {
        throw "Canonical Python environment not found at $python. Create .venv first."
    }
    $repoRoot = Split-Path $PSScriptRoot -Parent
    Push-Location $repoRoot
    try {
        & $python -m pip check
        Assert-LastExitCode "Dependency consistency check"
        & $python -m ruff check emergent_matter_model tools tests `
            --select W605,B023,F841,E741 `
            --per-file-ignores "emergent_matter_model/black_hole_horizon_entropy.py:F841,emergent_matter_model/sparc_bulge_test.py:B023"
        Assert-LastExitCode "Correctness lint check"
        & $python -m coverage run -m pytest -m "not golden" -q
        Assert-LastExitCode "Python test suite"
        & $python -m coverage report
        Assert-LastExitCode "Coverage report"
        & $python emergent_matter_model\emrf_cli.py doctor
        Assert-LastExitCode "EMRF doctor"
        & $python emergent_matter_model\emrf_cli.py data list --verify
        Assert-LastExitCode "Dataset verification"
        if ($env:EMRF_RUN_GOLDEN -eq "1") {
            & $python tools\run_golden_results.py --all
            Assert-LastExitCode "Golden-result suite"
        }
    } finally {
        Pop-Location
    }

    Write-Host "[2/4] Headless physics check" -ForegroundColor Cyan
    & $python compare_schwarzschild.py --headless
    Assert-LastExitCode "Headless physics check"

Write-Host "[3/4] Ensure Maven available" -ForegroundColor Cyan
$installMaven = Join-Path $PSScriptRoot "..\docs\install_maven.ps1"
if (Test-Path $installMaven) {
    & $installMaven
    Assert-LastExitCode "Maven setup"
}

Write-Host "[4/4] JavaFX compile" -ForegroundColor Cyan
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
        Assert-LastExitCode "JavaFX compile"
    } finally {
        Pop-Location
    }
}

    Write-Host "Local CI checks passed successfully." -ForegroundColor Green
} finally {
    Pop-Location
}
