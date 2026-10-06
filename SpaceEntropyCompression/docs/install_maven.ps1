# PowerShell script to download and install Maven on Windows
# This script will:
# 1. Download the latest Maven binary zip
# 2. Extract it to D:\Projects\gtd\tools\apache-maven
# 3. Add Maven to the system PATH for the current session

$ErrorActionPreference = 'Stop'

# Set variables
$mavenVersion = '3.9.6'
$mavenUrl = "https://archive.apache.org/dist/maven/maven-3/$mavenVersion/binaries/apache-maven-$mavenVersion-bin.zip"
$installDir = "D:\Projects\gtd\tools\apache-maven"
$zipPath = "$installDir\apache-maven-$mavenVersion-bin.zip"

# Create install directory if it doesn't exist
if (-not (Test-Path $installDir)) {
    New-Item -ItemType Directory -Path $installDir | Out-Null
}

# Download Maven zip if not already present
if (-not (Test-Path $zipPath)) {
    Invoke-WebRequest -Uri $mavenUrl -OutFile $zipPath
}

# Extract Maven
Expand-Archive -Path $zipPath -DestinationPath $installDir -Force

# Set Maven bin path
$mavenBin = Join-Path $installDir "apache-maven-$mavenVersion\bin"

# Add Maven to PATH for current session
$env:Path = "$mavenBin;" + $env:Path
$env:MAVEN_OPTS = "--enable-native-access=ALL-UNNAMED --sun-misc-unsafe-memory-access=allow -Djansi.mode=off"

# Verify Maven installation
mvn -v
