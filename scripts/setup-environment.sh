#!/usr/bin/env bash
set -e
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$script_dir/_common.sh"
cd "$workspace_root"

"$script_dir/clean-environment.sh"

echo "[TASK] Setting up environment in '$VENV_ROOT'..."

python3 -m venv "$VENV_ROOT"

"$PYTHON_EXE" -m pip install --upgrade pip
"$PYTHON_EXE" -m pip install --upgrade --force-reinstall build setuptools wheel mypy debugpy
"$PYTHON_EXE" -m pip install --upgrade --force-reinstall .[test]
"$PYTHON_EXE" -m pip --version
"$PYTHON_EXE" -m pip freeze

echo "[TASK] Environment setup complete."
