$ErrorActionPreference = "Stop"

# Determine repo root by climbing out of scripts dir
Set-Location "$PSScriptRoot/../../.."   # repo root

$TAG = Get-Date -Format "yyyyMMddHHmmss"
Write-Host "Using TAG: $TAG"

# Write terraform tag files
Set-Content -Path "web/trader_backend/.backend_tag" -Value $TAG
Set-Content -Path "web/trader_backend/backend.auto.tfvars" -Value "backend_tag = '$TAG'"

Write-Host "Building Docker image..."
docker build `
    -t perspectiv-trader-backend:latest `
    -f web/trader_backend/Dockerfile `
    .

Write-Host "Done."
Write-Host "Local image created: perspectiv-trader-backend:latest"
Write-Host "Tag used: $TAG"
