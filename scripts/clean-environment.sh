#!/usr/bin/env bash
set -e
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$script_dir/_common.sh"

echo "[TASK] Cleaning environment..."

if [ -d "$venv_root" ]; then
  echo "Removing stale venv at '$venv_root'..."
  rm -rf "$venv_root"
  echo "Stale venv removed."
fi

echo "[TASK] Environment cleaned."
