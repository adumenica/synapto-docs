# sync-docs.ps1
# Syncs documentation from the local Synapto source to the content/docs folder

$source = "C:\Users\AlinD\Documents\GitHub\Synapto\docs"
$destination = "$PSScriptRoot\content\docs"

if (-not (Test-Path $source)) {
    Write-Error "Source path not found: $source"
    exit 1
}

Write-Host "Syncing docs from $source to $destination..." -ForegroundColor Cyan

# Create destination if it doesn't exist
if (-not (Test-Path $destination)) {
    New-Item -ItemType Directory -Path $destination -Force | Out-Null
}

# Copy files (recursive)
Copy-Item -Path "$source\*" -Destination $destination -Recurse -Force

Write-Host "Sync complete!" -ForegroundColor Green
