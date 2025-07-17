#!/usr/bin/env bash
set -e
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$script_dir/_common.sh"

# Load UV
source $HOME/.local/bin/env

# Run dependencies
"$script_dir/clean-package.sh"

# Build wheel
echo "[TASK] Building package wheel..."
"$PYTHON_EXE" -m build --sdist --wheel --installer uv
wheel=$(ls -t "$WORKSPACE_ROOT"/dist/*.whl | head -n1)
echo "[TASK] Package wheel built."
