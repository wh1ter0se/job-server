param()
. "$PSScriptRoot/_common.ps1"


# Make sure we run from repo root
Set-Location $workspaceRoot

# 0. Clean any old venv
& (Join-Path $PSScriptRoot 'clean-environment.ps1')

echo "[TASK] Setting up environment in '$venvRoot'..."

# 1. Create a fresh venv
python -m venv $venvRoot

# 2. Upgrade pip
& $pythonExe -m pip install --upgrade pip

# 3. Reinstall build tools
& $pythonExe -m pip install --upgrade --force-reinstall build setuptools wheel mypy debugpy

# 4. Install test deps
& $pythonExe -m pip install --upgrade --force-reinstall .[test]

# 5. Show pip version & freeze
& $pythonExe -m pip --version
& $pythonExe -m pip freeze

echo "[TASK] Environment setup complete."