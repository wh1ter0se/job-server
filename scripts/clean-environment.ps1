param()
. "$PSScriptRoot/_common.ps1"

echo "[TASK] Cleaning environment..."

# Remove the virtual environment if it exists
if (Test-Path $venvRoot) {
    echo "Removing stale venv at '$venvRoot'..."
    Remove-Item -Recurse -Force $venvRoot
    echo "Stale venv removed."
}

echo "[TASK] Environment cleaned."
