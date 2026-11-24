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

Write-Host "[3/4] Configure Java" -ForegroundColor Cyan
if (-not $env:JAVA_HOME -or -not (Test-Path (Join-Path $env:JAVA_HOME "bin\javac.exe"))) {
    $env:JAVA_HOME = $null
    $javacCmd = Get-Command javac -ErrorAction SilentlyContinue
    if ($javacCmd) {
        $candidate = Split-Path (Split-Path $javacCmd.Source -Parent) -Parent
        if (Test-Path (Join-Path $candidate "bin\javac.exe")) {
            $env:JAVA_HOME = $candidate
        }
    }
    if (-not $env:JAVA_HOME) {
        $jdkRoot = Get-ChildItem -Path "G:\Program Files\Java", "C:\Program Files\Java", "C:\Program Files\Eclipse Adoptium", "C:\Program Files\Microsoft" -Directory -Filter "jdk*" -ErrorAction SilentlyContinue |
            Where-Object { Test-Path (Join-Path $_.FullName "bin\javac.exe") } |
            Sort-Object Name -Descending |
            Select-Object -First 1
        if ($jdkRoot) {
            $env:JAVA_HOME = $jdkRoot.FullName
        }
    }
}
if ($env:JAVA_HOME -and (Test-Path $env:JAVA_HOME)) {
    $env:Path = "$env:JAVA_HOME\bin;" + $env:Path
}

$javafxDir = Join-Path $PSScriptRoot "javafx_client"
if (Test-Path $javafxDir) {
    Write-Host "[4/4] JavaFX contract tests" -ForegroundColor Cyan
    Push-Location $javafxDir
    try {
        & ".\mvnw.cmd" --batch-mode --no-transfer-progress test
        Assert-LastExitCode "JavaFX contract tests"
    } finally {
        Pop-Location
    }
}

    Write-Host "Local CI checks passed successfully." -ForegroundColor Green
} finally {
    Pop-Location
}
