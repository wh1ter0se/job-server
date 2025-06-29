param([switch]$Production)
. "$PSScriptRoot/_common.ps1"
Set-Location $workspaceRoot

# 0. Clean + regenerate stubs
& (Join-Path $PSScriptRoot 'clean-package.ps1')
& (Join-Path $PSScriptRoot 'generate-stubs.ps1')

echo "[TASK] Building and installing package..."

if ($Production) {
    echo "Installing in production mode..."
    # 1. Build sdist + wheel
    & $pythonExe -m build --sdist --wheel

    # 2. Pick the newest wheel
    $wheel = Get-ChildItem -Path (Join-Path $workspaceRoot 'dist') -Filter '*.whl' |
            Select-Object -Last 1 -ExpandProperty FullName

    # 3. Install that wheel
    & $pythonExe -m pip install --force-reinstall $wheel
}
else {
    echo "Installing in editable mode for debug..."
    & $pythonExe -m pip install --force-reinstall -e $workspaceRoot
}

# 4. Show pip version & freeze
& $pythonExe -m pip --version
& $pythonExe -m pip freeze

echo "[TASK] Package built and installed."