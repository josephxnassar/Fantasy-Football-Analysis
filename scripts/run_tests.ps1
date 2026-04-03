$repoRoot = Split-Path -Parent $PSScriptRoot

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "uv is not installed or not on PATH." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Running Backend Tests" -ForegroundColor Cyan
Write-Host "Target: backend\tests" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Set-Location -LiteralPath $repoRoot
uv run python -m pytest -v backend/tests
$exitCode = $LASTEXITCODE

if ($exitCode -ne 0) {
    Write-Host "Tests failed." -ForegroundColor Red
    exit $exitCode
}

Write-Host "All backend tests passed." -ForegroundColor Green
