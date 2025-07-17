#!/usr/bin/env bash
set -e
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$script_dir/_common.sh"
cd "$workspace_root"

"$script_dir/clean-environment.sh"

echo "[TASK] Setting up environment in '$VENV_ROOT'..."

uv venv "$VENV_ROOT"

uv pip install --python "$PYTHON_EXE" --upgrade build setuptools wheel mypy debugpy
uv pip install --python "$PYTHON_EXE" --upgrade --editable "$WORKSPACE_ROOT[test]"
uv pip list --python "$PYTHON_EXE"

echo "[TASK] Environment setup complete."
