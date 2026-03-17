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

function Refresh-GitIndexMetadata {
    # OneDrive-backed worktrees can leave Git's cached file metadata stale after
    # formatter runs even when file contents did not actually change.
    & git -C $repoRoot update-index --really-refresh 2>$null | Out-Null
    $global:LASTEXITCODE = 0
}

function Show-RealDiffSummary {
    $changedFiles = @(git -C $repoRoot diff --name-only)
    $shortStat = ((git -C $repoRoot diff --shortstat) | Out-String).Trim()

    Write-Host ""
    if ($changedFiles.Count -eq 0) {
        Write-Host "No content changes remain after autofix." -ForegroundColor Green
        return
    }

    Write-Host "Real content changes after autofix:" -ForegroundColor Yellow
    foreach ($file in $changedFiles) {
        Write-Host " - $file"
    }

    if ($shortStat) {
        Write-Host $shortStat -ForegroundColor DarkGray
    }
}

Write-Host "Running autofix commands from $repoRoot" -ForegroundColor Yellow

Invoke-Step "Backend lint autofix (ruff)" { uv run ruff check --fix backend }
Invoke-Step "Frontend lint autofix (eslint)" { Invoke-InFrontend { npm run lint:fix } }
Invoke-Step "Frontend format (prettier)" { Invoke-InFrontend { npm run format } }

Refresh-GitIndexMetadata
Show-RealDiffSummary

Write-Host ""
Write-Host "Autofix commands completed." -ForegroundColor Green
