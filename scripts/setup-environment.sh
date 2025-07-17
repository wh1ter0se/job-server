#!/usr/bin/env bash
set -e
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$script_dir/_common.sh"

# Clean the environment
"$script_dir/clean-environment.sh"

echo "[TASK] Setting up environment in '$VENV_ROOT'..."

# Instal UV
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env

# Install Python
uv python install 3.12

# Setup venv
uv venv "$VENV_ROOT"
uv pip install --python "$PYTHON_EXE" --upgrade build wheel mypy debugpy

# Generate the stubs
"$script_dir/generate-stubs.sh"

# Install the package in editable mode
uv pip install --python "$PYTHON_EXE" --upgrade --editable "$WORKSPACE_ROOT[test]"
uv pip list --python "$PYTHON_EXE"

echo "[TASK] Environment setup complete."
