#!/usr/bin/env bash
set -e
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$script_dir/_common.sh"

# Run dependency
"$script_dir/rebuild-package.sh"

# Run tests
echo "[TASK] Running tests..."
"$PYTHON_EXE" -m pytest tests
echo "[TASK] Finished running tests."
