[CmdletBinding()]
param(
    [switch]$SkipPythonSync,
    [switch]$SkipFrontendInstall,
    [switch]$SetupOnly
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition
$repoRoot = Split-Path -Parent -Path $scriptDir
$frontendPath = Join-Path $repoRoot "frontend"
Set-Location $repoRoot

function Assert-CommandAvailable {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name,

        [Parameter(Mandatory = $true)]
        [string]$InstallHint
    )

    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        Write-Host "Missing required command: $Name" -ForegroundColor Red
        Write-Host $InstallHint -ForegroundColor Yellow
        exit 1
    }

    $version = & $Name --version 2>&1
    Write-Host "Found ${Name}: $version" -ForegroundColor Green
}

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

function Start-DevTerminal {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Title,

        [Parameter(Mandatory = $true)]
        [string]$CommandLine
    )

    $wrappedCommand = "title $Title && $CommandLine"
    Start-Process cmd.exe -ArgumentList "/k", $wrappedCommand -WindowStyle Normal
}

Write-Host "Starting development setup from $repoRoot" -ForegroundColor Yellow

Invoke-Step "Tool check: uv" {
    Assert-CommandAvailable `
        -Name "uv" `
        -InstallHint "Install uv from https://docs.astral.sh/uv/"
}

Invoke-Step "Tool check: Node.js" {
    Assert-CommandAvailable `
        -Name "node" `
        -InstallHint "Install Node.js 18+ from https://nodejs.org/"
}

if (-not $SkipPythonSync) {
    Invoke-Step "Python dependencies (uv sync)" { uv sync }
} else {
    Write-Host ""
    Write-Host "Skipping Python sync (--SkipPythonSync)." -ForegroundColor Yellow
}

if (-not (Test-Path -LiteralPath $frontendPath)) {
    Write-Host "Frontend directory not found: $frontendPath" -ForegroundColor Red
    exit 1
}

if (-not $SkipFrontendInstall) {
    $nodeModulesPath = Join-Path $frontendPath "node_modules"
    if (Test-Path -LiteralPath $nodeModulesPath) {
        Write-Host ""
        Write-Host "Frontend dependencies already present (node_modules)." -ForegroundColor Green
    } else {
        Invoke-Step "Frontend dependencies (npm install)" { npm --prefix frontend install }
    }
} else {
    Write-Host ""
    Write-Host "Skipping frontend install (--SkipFrontendInstall)." -ForegroundColor Yellow
}

if ($SetupOnly) {
    Write-Host ""
    Write-Host "Setup complete. Server launch skipped (--SetupOnly)." -ForegroundColor Green
    exit 0
}

Write-Host ""
Write-Host "=== Launching Development Servers ===" -ForegroundColor Cyan

$backendCmd = "cd /d `"$repoRoot`" && uv run python -m backend.run_api"
$frontendCmd = "cd /d `"$frontendPath`" && npm run dev"

Start-DevTerminal -Title "Fantasy API" -CommandLine $backendCmd
Start-Sleep -Seconds 2
Start-DevTerminal -Title "Fantasy Frontend" -CommandLine $frontendCmd

Write-Host ""
Write-Host "Backend API: http://localhost:8000" -ForegroundColor Yellow
Write-Host "Frontend:    http://localhost:3000" -ForegroundColor Yellow
Write-Host ""
Write-Host "To stop: Ctrl+C in each launched terminal window." -ForegroundColor Gray
