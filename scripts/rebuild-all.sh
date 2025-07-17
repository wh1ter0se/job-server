#!/usr/bin/env bash
set -e
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "[TASK] Starting full rebuild..."

"$script_dir/setup-environment.sh"
"$script_dir/rebuild-package.sh"

echo "[TASK] Full rebuild complete."
