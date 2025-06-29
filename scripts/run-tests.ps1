param()
. "$PSScriptRoot/_common.ps1"
Set-Location $workspaceRoot

echo "[TASK] Running tests..."

# Run pytest on the test directory
& $pythonExe -m pytest test

echo "[TASK] Finished running tests."