[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition
$repoRoot = Split-Path -Parent -Path $scriptDir
Set-Location $repoRoot

function Invoke-Step {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name,

        [Parameter(Mandatory = $true)]
        [scriptblock]$Action
    )

    Write-Host ""
    Write-Host "=== $Name ===" -ForegroundColor Cyan
    & $Action

    if ($LASTEXITCODE -ne 0) {
        Write-Host "FAILED: $Name" -ForegroundColor Red
        exit $LASTEXITCODE
    }

    Write-Host "PASSED: $Name" -ForegroundColor Green
}

function Invoke-InFrontend {
    param(
        [Parameter(Mandatory = $true)]
        [scriptblock]$Action
    )

    Push-Location (Join-Path $repoRoot "frontend")
    try {
        & $Action
    } finally {
        Pop-Location
    }
}

Write-Host "Running autofix commands from $repoRoot" -ForegroundColor Yellow

Invoke-Step "Backend lint autofix (ruff)" { uv run ruff check --fix backend }
Invoke-Step "Frontend lint autofix (eslint)" { Invoke-InFrontend { npm run lint:fix } }
Invoke-Step "Frontend format (prettier)" { Invoke-InFrontend { npm run format } }

Write-Host ""
Write-Host "Autofix commands completed." -ForegroundColor Green
