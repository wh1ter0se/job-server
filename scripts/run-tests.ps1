param()
. "$PSScriptRoot/_common.ps1"
Set-Location $workspaceRoot

& (Join-Path $PSScriptRoot 'rebuild-install-package.ps1')

echo "[TASK] Running tests..."

# Run pytest on the test directory
& $pythonExe -m pytest tests

echo "[TASK] Finished running tests."