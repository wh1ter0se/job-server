param()
. "$PSScriptRoot/_common.ps1"
Set-Location $workspaceRoot

echo "[TASK] Generating stubs..."

# Remove old stubs
$stubsDir = Join-Path $workspaceRoot 'src/jobserver/stubs'
if (Test-Path $stubsDir) {
    echo "Removing old stubs at '$stubsDir'..."
    Remove-Item -Recurse -Force $stubsDir
    echo "Old stubs removed."
}

# Generate new stubs
echo "Generating new stubs at '$stubsDir'..."
& $stubgenExe --no-import -o $stubsDir (Join-Path $workspaceRoot 'src/jobserver') 2>&1
echo "New stubs generated."

echo "[TASK] Stubs generated."