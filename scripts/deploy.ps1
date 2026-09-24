$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================"
Write-Host "       BUILDING LAMBDA PACKAGE"
Write-Host "========================================"

if (Test-Path "build") {
    Remove-Item -Recurse -Force "build"
}

New-Item -ItemType Directory -Path "build" | Out-Null
New-Item -ItemType Directory -Path "build\lambda" | Out-Null

Copy-Item `
    "lambda\lambda_function.py" `
    "build\lambda\lambda_function.py"

Write-Host ""
Write-Host "Installing Linux dependencies..."

docker run --rm `
    -v "${PWD}\build\lambda:/var/task" `
    python:3.12-slim `
    bash -c "pip install Pillow -t /var/task"

Write-Host ""
Write-Host "Creating ZIP..."

Compress-Archive `
    -Path "build\lambda\*" `
    -DestinationPath "build\lambda.zip" `
    -Force

Write-Host ""
Write-Host "Lambda package created:"
Write-Host "build\lambda.zip"

Write-Host ""
Write-Host "========================================"
Write-Host "             BUILD COMPLETE"
Write-Host "========================================"