# Local CI equivalent for environments without GitHub Actions
# Runs Python unit tests and JavaFX Maven compile.

$ErrorActionPreference = 'Stop'

Write-Host "[1/3] Python tests" -ForegroundColor Cyan
& 'G:\Program Files\Python314\python.exe' -m pytest test_model.py test_server_api.py -v

Write-Host "[2/3] Ensure Maven available" -ForegroundColor Cyan
& "$PSScriptRoot\..\install_maven.ps1"

Write-Host "[3/3] JavaFX compile" -ForegroundColor Cyan
$env:JAVA_HOME = 'G:\Program Files\Java\jdk-25.0.2'
$env:Path = "$env:JAVA_HOME\bin;" + $env:Path
Set-Location "$PSScriptRoot\javafx_client"
mvn -DskipTests compile

Write-Host "Local CI checks passed." -ForegroundColor Green
