# Fantasy Football Analysis - Full Quality Gate
# Runs backend + frontend quality checks in fail-fast order.

[CmdletBinding()]
param(
    [switch]$SkipBuild
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition
$repoRoot = Split-Path -Parent -Path $scriptDir
Set-Location $repoRoot

function Invoke-QualityStep {
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

Write-Host "Running full quality gate from $repoRoot" -ForegroundColor Yellow

Invoke-QualityStep "Backend lint (ruff)" { uv run ruff check backend }
Invoke-QualityStep "Backend type check (mypy)" { uv run mypy }
Invoke-QualityStep "Backend tests (pytest)" { uv run pytest -q backend/tests }
Invoke-QualityStep "Frontend lint" { Invoke-InFrontend { npm run lint } }
Invoke-QualityStep "Frontend tests" { Invoke-InFrontend { npm run test:run } }
Invoke-QualityStep "Frontend audit" { Invoke-InFrontend { npm audit } }

if (-not $SkipBuild) {
    Invoke-QualityStep "Frontend build" { Invoke-InFrontend { npm run build } }
} else {
    Write-Host ""
    Write-Host "Skipping frontend build (--SkipBuild)." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Quality gate passed." -ForegroundColor Green
