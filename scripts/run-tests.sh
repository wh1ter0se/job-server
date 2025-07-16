#!/usr/bin/env bash
set -e
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$script_dir/_common.sh"
cd "$workspace_root"

"$script_dir/rebuild-install-package.sh"

echo "[TASK] Running tests..."
"$python_exe" -m pytest tests

echo "[TASK] Finished running tests."
