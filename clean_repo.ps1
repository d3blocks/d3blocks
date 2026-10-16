# clean_repo.ps1

# Directories to remove from the Git repository

$patterns = @(
"*.egg-info",
"dist",
"build"
)

# Find the root of the current Git repository

$repo = git rev-parse --show-toplevel 2>$null

if (-not $repo) {
Write-Host "Error: not inside a Git repository." -ForegroundColor Red
Read-Host "Press Enter to exit"
exit 1
}

$repo = $repo.Trim()

Write-Host "Git repository: $repo" -ForegroundColor Cyan
Write-Host ""

# Find directories to clean

$folders = @()

foreach ($pattern in $patterns) {
$folders += Get-ChildItem -Path $repo -Directory -Recurse -Force -Filter $pattern
}

# Remove duplicates

$folders = $folders | Sort-Object FullName -Unique

if ($folders.Count -eq 0) {
Write-Host "No directories found to clean." -ForegroundColor Green
Write-Host ""
Read-Host "Press Enter to exit"
exit 0
}

# Show directories

Write-Host "The following directories will be removed:" -ForegroundColor Yellow
Write-Host ""

foreach ($folder in $folders) {
Write-Host "  $($folder.FullName)"
}

Write-Host ""

$answer = Read-Host "Press Enter to continue, or N/Q to abort"

if ($answer -match "^[nq]$") {
Write-Host ""
Write-Host "Cleanup cancelled." -ForegroundColor Yellow
Read-Host "Press Enter to exit"
exit 0
}

Write-Host ""
Write-Host "Cleaning..." -ForegroundColor Cyan

foreach ($folder in $folders) {
Write-Host "Removing: $($folder.FullName)"
Remove-Item -LiteralPath $folder.FullName -Recurse -Force
}

Write-Host ""
Write-Host "Done." -ForegroundColor Green

Read-Host "Press Enter to exit"
