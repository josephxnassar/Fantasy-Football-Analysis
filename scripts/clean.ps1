$repoRoot = Split-Path -Parent $PSScriptRoot
$venvRoot = Join-Path $repoRoot ".venv"
$venvPattern = "$venvRoot\*"
$targets = @(
    "__pycache__"
    ".pytest_cache"
    ".mypy_cache"
    ".ruff_cache"
    ".uv-cache"
)

$directories = Get-ChildItem -LiteralPath $repoRoot -Directory -Recurse -Force |
    Where-Object { $targets -contains $_.Name -and $_.FullName -notlike $venvPattern } |
    Sort-Object { $_.FullName.Length } -Descending

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Cleaning Temp Directories" -ForegroundColor Cyan
Write-Host "Repo: $repoRoot" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

if (-not $directories) {
    Write-Host "No temp directories found." -ForegroundColor Yellow
    exit 0
}

$removedCount = 0

foreach ($directory in $directories) {
    Remove-Item -LiteralPath $directory.FullName -Recurse -Force
    Write-Host "Removed $($directory.FullName)" -ForegroundColor Green
    $removedCount++
}

Write-Host "Removed $removedCount targets." -ForegroundColor Green
