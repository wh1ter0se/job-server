param()
. "$PSScriptRoot/_common.ps1"
Set-Location $workspaceRoot

echo "[TASK] Running tests..."

# Run pytest on the test directory
& $pythonExe -m pytest tests

echo "[TASK] Finished running tests."