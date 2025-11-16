$ErrorActionPreference = "Stop"

# Determine repo root by climbing out of scripts dir
Set-Location "$PSScriptRoot/../../.."   # now you're at repo root

$AWS_REGION = "us-west-2"
$ECR_REPO   = "451747690945.dkr.ecr.$AWS_REGION.amazonaws.com/perspectiv-trader-backend"

Write-Host "Authenticating to ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REPO

$TAG = Get-Date -Format "yyyyMMddHHmmss"
Write-Host "Using TAG: $TAG"

# Write terraform tag files
Set-Content -Path "web/trader_backend/.backend_tag" -Value $TAG
Set-Content -Path "web/trader_backend/backend.auto.tfvars" -Value "backend_tag = '$TAG'"

Write-Host "Building Docker image with -f..."
docker build `
    -t perspectiv-trader-backend:latest `
    -f web/trader_backend/Dockerfile `
    .

Write-Host "Tagging image..."
docker tag perspectiv-trader-backend:latest "${ECR_REPO}:${TAG}"

Write-Host "Pushing image..."
docker push "${ECR_REPO}:${TAG}"

Write-Host "Done."
Write-Host "Image pushed: ${ECR_REPO}:${TAG}"
