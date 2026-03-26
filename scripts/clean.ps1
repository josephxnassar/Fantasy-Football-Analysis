$repoRoot = Split-Path -Parent $PSScriptRoot
$venvRoot = Join-Path $repoRoot ".venv"
$venvPattern = "$venvRoot\*"
$targets = @(
    "__pycache__"
    ".ruff_cache"
    ".mypy_cache"
    ".uv-cache"
)

$directories = Get-ChildItem -LiteralPath $repoRoot -Directory -Recurse -Force |
    Where-Object { $targets -contains $_.Name -and $_.FullName -notlike $venvPattern } |
    Sort-Object { $_.FullName.Length } -Descending

Write-Host "Cleaning temp directories from $repoRoot" -ForegroundColor Cyan

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
