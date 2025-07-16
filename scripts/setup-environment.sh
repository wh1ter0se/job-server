#!/usr/bin/env bash
set -e
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$script_dir/_common.sh"
cd "$workspace_root"

"$script_dir/clean-environment.sh"

echo "[TASK] Setting up environment in '$venv_root'..."

python -m venv "$venv_root"

"$python_exe" -m pip install --upgrade pip
"$python_exe" -m pip install --upgrade --force-reinstall build setuptools wheel mypy debugpy
"$python_exe" -m pip install --upgrade --force-reinstall .[test]
"$python_exe" -m pip --version
"$python_exe" -m pip freeze

echo "[TASK] Environment setup complete."
