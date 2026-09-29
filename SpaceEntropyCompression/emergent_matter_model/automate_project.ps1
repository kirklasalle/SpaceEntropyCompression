# automate_project.ps1
#
# DEPRECATED — use run_all.ps1 instead.
# This file is kept for backward compatibility and simply delegates.

Write-Host "NOTE: automate_project.ps1 is deprecated. Use run_all.ps1 instead." -ForegroundColor Yellow
& "$PSScriptRoot\run_all.ps1" @args
