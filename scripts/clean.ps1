[CmdletBinding()]
param(
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition
$repoRoot = Split-Path -Parent -Path $scriptDir
Set-Location $repoRoot

function Remove-Target {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        return $false
    }

    if ($DryRun) {
        Write-Host "DRY RUN: would remove $Path" -ForegroundColor Yellow
    } else {
        Remove-Item -LiteralPath $Path -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "Removed $Path" -ForegroundColor Green
    }

    return $true
}

Write-Host "Cleaning local cache/build artifacts from $repoRoot" -ForegroundColor Cyan

$explicitTargets = @(
    ".pytest_cache",
    ".pytest_tmp",
    ".ruff_cache",
    ".mypy_cache",
    ".eslintcache",
    "frontend/.vite",
    "frontend/dist",
    "frontend/coverage",
    "frontend/node_modules/.cache",
    "backend/tests/tmp_pytest",
    "backend/tests/tmp_pytest_runtime",
    "backend/tests/tmp_mypy_cache",
    "backend/tests/.pytest_work",
    ".coverage",
    "htmlcov"
)

$removedCount = 0

foreach ($target in $explicitTargets) {
    if (Remove-Target -Path $target) {
        $removedCount++
    }
}

$pythonScanRoots = @(
    "backend",
    "scripts"
)

foreach ($root in $pythonScanRoots) {
    if (-not (Test-Path -LiteralPath $root)) {
        continue
    }

    $pycacheDirs = Get-ChildItem -Path $root -Recurse -Force -Directory -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -eq "__pycache__" }

    foreach ($dir in $pycacheDirs) {
        if (Remove-Target -Path $dir.FullName) {
            $removedCount++
        }
    }

    $bytecodeFiles = Get-ChildItem -Path $root -Recurse -Force -File -Include "*.pyc","*.pyo" -ErrorAction SilentlyContinue

    foreach ($file in $bytecodeFiles) {
        if (Remove-Target -Path $file.FullName) {
            $removedCount++
        }
    }
}

if ($DryRun) {
    Write-Host "Dry run complete. Targets found: $removedCount" -ForegroundColor Yellow
} else {
    Write-Host "Clean complete. Targets removed: $removedCount" -ForegroundColor Green
}
