#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Deploy script for Log Lady (Alexa + Notion Skill)

.DESCRIPTION
    Builds, tests, packages, and deploys the Lambda function.
    Publishes a new version for rollback support.

.PARAMETER SkipTests
    Skip running pytest before deploy (not recommended)

.PARAMETER FunctionName
    Lambda function name (default: alexa-notion-skill)

.PARAMETER Region
    AWS region (default: eu-west-1)

.EXAMPLE
    ./deploy.ps1
    ./deploy.ps1 -FunctionName "my-lambda" -Region "us-east-1"
#>

param(
    [switch]$SkipTests,
    [string]$FunctionName = "alexa-notion-skill",
    [string]$Region = "eu-west-1"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot
$LambdaDir = Join-Path $ProjectRoot "lambda"
$PackageDir = Join-Path $LambdaDir "package"
$ZipPath = Join-Path $ProjectRoot "lambda-deployment.zip"

Write-Host ""
Write-Host "=== Log Lady Deploy ===" -ForegroundColor Cyan
Write-Host "Function: $FunctionName"
Write-Host "Region:   $Region"
Write-Host ""

# --- Step 1: Run tests ---
if (-not $SkipTests) {
    Write-Host "[1/5] Running tests..." -ForegroundColor Yellow
    Push-Location $ProjectRoot
    python -m pytest --tb=short -q
    if ($LASTEXITCODE -ne 0) {
        Write-Host "TESTS FAILED. Deploy aborted." -ForegroundColor Red
        Pop-Location
        exit 1
    }
    Pop-Location
    Write-Host "  Tests passed!" -ForegroundColor Green
} else {
    Write-Host "[1/5] Skipping tests (--SkipTests)" -ForegroundColor DarkYellow
}

# --- Step 2: Clean package directory ---
Write-Host "[2/5] Cleaning package..." -ForegroundColor Yellow
if (Test-Path $PackageDir) {
    # Remove __pycache__ directories
    Get-ChildItem -Path $PackageDir -Directory -Filter "__pycache__" -Recurse |
        Remove-Item -Recurse -Force
}

# --- Step 3: Copy source files to package ---
Write-Host "[3/5] Copying source to package..." -ForegroundColor Yellow
$SourceFiles = @(
    "lambda_function.py",
    "config.py",
    "routing.py",
    "notion_client.py",
    "messages.py"
)
foreach ($file in $SourceFiles) {
    $src = Join-Path $LambdaDir $file
    $dst = Join-Path $PackageDir $file
    if (Test-Path $src) {
        Copy-Item $src -Destination $dst -Force
    } else {
        Write-Host "  ERROR: $file not found in lambda/" -ForegroundColor Red
        exit 1
    }
}
Write-Host "  Copied $($SourceFiles.Count) source files" -ForegroundColor Green

# --- Step 4: Create ZIP ---
Write-Host "[4/5] Creating deployment ZIP..." -ForegroundColor Yellow
if (Test-Path $ZipPath) {
    Remove-Item $ZipPath -Force
}
Compress-Archive -Path "$PackageDir\*" -DestinationPath $ZipPath -Force
$zipSize = [math]::Round((Get-Item $ZipPath).Length / 1MB, 2)
Write-Host "  Created: lambda-deployment.zip ($zipSize MB)" -ForegroundColor Green

# --- Step 5: Upload to Lambda and publish version ---
Write-Host "[5/5] Uploading to Lambda..." -ForegroundColor Yellow
try {
    $updateResult = aws lambda update-function-code `
        --function-name $FunctionName `
        --zip-file "fileb://$ZipPath" `
        --region $Region `
        --output json 2>&1 | ConvertFrom-Json

    Write-Host "  Uploaded successfully" -ForegroundColor Green

    # Wait for update to complete
    Write-Host "  Waiting for function to be ready..." -ForegroundColor DarkYellow
    aws lambda wait function-updated --function-name $FunctionName --region $Region

    # Publish a new version
    $versionResult = aws lambda publish-version `
        --function-name $FunctionName `
        --region $Region `
        --description "Deploy $(Get-Date -Format 'yyyy-MM-dd HH:mm')" `
        --output json 2>&1 | ConvertFrom-Json

    $version = $versionResult.Version
    Write-Host "  Published version: $version" -ForegroundColor Green
    Write-Host ""
    Write-Host "=== Deploy complete! ===" -ForegroundColor Cyan
    Write-Host "  Version: $version"
    Write-Host "  Rollback: aws lambda update-function-configuration --function-name $FunctionName --region $Region"
    Write-Host ""
}
catch {
    Write-Host "  ERROR: Deploy failed!" -ForegroundColor Red
    Write-Host "  $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "  Common issues:" -ForegroundColor Yellow
    Write-Host "    - AWS CLI not installed or configured"
    Write-Host "    - Wrong function name or region"
    Write-Host "    - Insufficient IAM permissions"
    exit 1
}
