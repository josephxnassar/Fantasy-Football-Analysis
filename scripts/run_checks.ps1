$repoRoot = Split-Path -Parent $PSScriptRoot

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "uv is not installed or not on PATH." -ForegroundColor Red
    exit 1
}

Set-Location -LiteralPath $repoRoot

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Running ruff check on backend" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
uv run ruff check backend
$exitCode = $LASTEXITCODE

if ($exitCode -ne 0) {
    Write-Host "Ruff check failed." -ForegroundColor Red
    exit $exitCode
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Running mypy on backend" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
uv run mypy
$exitCode = $LASTEXITCODE

if ($exitCode -ne 0) {
    Write-Host "Mypy check failed." -ForegroundColor Red
    exit $exitCode
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Running backend/tests" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
uv run python -m pytest backend/tests
$exitCode = $LASTEXITCODE

if ($exitCode -ne 0) {
    Write-Host "Tests failed." -ForegroundColor Red
    exit $exitCode
}

Write-Host "All backend checks passed." -ForegroundColor Green
