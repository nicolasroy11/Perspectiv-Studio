$ErrorActionPreference = "Stop"

# Generate timestamp tag
$TAG = Get-Date -Format "yyyyMMddHHmmss"

# Write tag to files
Set-Content -Path ".backend_tag" -Value $TAG
Set-Content -Path "backend.auto.tfvars" -Value "backend_tag = `"$TAG`""

Write-Host "TAG: $TAG"

# Tag Docker image
docker tag perspectiv-trader-backend:latest `
    451747690945.dkr.ecr.us-west-2.amazonaws.com/perspectiv-trader-backend:$TAG
