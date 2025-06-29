param()
. "$PSScriptRoot/_common.ps1"
Set-Location $workspaceRoot

echo "[TASK] Cleaning package artifacts..."

# Remove build artifacts
$buildDir = Join-Path $workspaceRoot 'build'
if (Test-Path $buildDir) {
    echo "Cleaning build folder at '$buildDir..."
    Remove-Item -Recurse -Force $buildDir
    echo "Build folder cleaned."
}

# Remove dist artifacts
$distDir = Join-Path $workspaceRoot 'dist'
if (Test-Path $distDir) {
    echo "Cleaning dist folder at '$distDir..."
    Remove-Item -Recurse -Force $distDir
    echo "Dist folder cleaned."
}

echo "[TASK] Package artifacts cleaned."
