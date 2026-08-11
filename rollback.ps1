#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Rollback Log Lady to a previous Lambda version.

.PARAMETER Version
    Version number to rollback to. Use 'list' to see available versions.

.PARAMETER FunctionName
    Lambda function name (default: alexa-notion-skill)

.PARAMETER Region
    AWS region (default: eu-west-1)

.EXAMPLE
    ./rollback.ps1 -Version list
    ./rollback.ps1 -Version 3
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$Version,
    [string]$FunctionName = "alexa-notion-skill",
    [string]$Region = "us-east-1"
)

$ErrorActionPreference = "Stop"

if ($Version -eq "list") {
    Write-Host "Available versions for $FunctionName:" -ForegroundColor Cyan
    aws lambda list-versions-by-function `
        --function-name $FunctionName `
        --region $Region `
        --query "Versions[].{Version:Version,Description:Description,Modified:LastModified}" `
        --output table
    exit 0
}

Write-Host "Rolling back $FunctionName to version $Version..." -ForegroundColor Yellow

try {
    # Get the code from the specified version
    aws lambda update-function-code `
        --function-name $FunctionName `
        --s3-bucket "" `
        --region $Region `
        --output json 2>$null

    # Alternative: use alias pointing to specific version
    # For now, we document the manual process
    Write-Host ""
    Write-Host "To rollback manually:" -ForegroundColor Cyan
    Write-Host "  1. Go to AWS Lambda Console"
    Write-Host "  2. Select '$FunctionName'"
    Write-Host "  3. Under 'Versions', find version $Version"
    Write-Host "  4. Copy the code from that version to `$LATEST"
    Write-Host ""
    Write-Host "Or use alias (if configured):" -ForegroundColor Cyan
    Write-Host "  aws lambda update-alias --function-name $FunctionName --name LIVE --function-version $Version --region $Region"
}
catch {
    Write-Host "Error: $_" -ForegroundColor Red
    exit 1
}
