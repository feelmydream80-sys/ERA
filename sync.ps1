param(
    [string]$Message = "auto: sync papers.db + code"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = "C:\dev\daq"

Write-Host "=== Sync: Crawl -> Commit -> Push ===" -ForegroundColor Cyan
Write-Host ""

# 1. Run all crawlers
Write-Host "[1/4] Running crawlers..." -ForegroundColor Yellow
$python = Join-Path $ProjectRoot "venv\Scripts\python.exe"

$script = @"
import sys
sys.path.insert(0, r'$ProjectRoot')
from app import create_app
from app.scheduler import run_all_crawlers
app = create_app()
results = run_all_crawlers(app)
for name, count in results.items():
    print(f'  {name}: {count} new papers')
total = sum(results.values())
print(f'  Total new: {total}')
"@

$totalNew = & $python -c $script
if ($LASTEXITCODE -ne 0) { throw "Crawler failed" }
Write-Host ""
Write-Host "  (output above from APScheduler)"

# 2. Stage all changes (code + papers.db)
Write-Host "[2/4] Staging files..." -ForegroundColor Yellow
Set-Location $ProjectRoot
git add -A
$status = git status --porcelain
if (-not $status) {
    Write-Host "  No changes to commit." -ForegroundColor Green
    exit 0
}
Write-Host $status
Write-Host ""

# 3. Commit
Write-Host "[3/4] Committing..." -ForegroundColor Yellow
if ($totalNew -and [int]$totalNew -gt 0) {
    $commitMsg = "$Message ($totalNew new papers)"
} else {
    $commitMsg = $Message
}
git commit -m $commitMsg
Write-Host ""

# 4. Push
Write-Host "[4/4] Pushing to GitHub..." -ForegroundColor Yellow
git push origin master
Write-Host ""

Write-Host "=== Sync complete ===" -ForegroundColor Cyan
