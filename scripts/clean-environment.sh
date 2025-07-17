#!/usr/bin/env bash
set -e
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$script_dir/_common.sh"

echo "[TASK] Cleaning environment..."

if [ -d "$VENV_ROOT" ]; then
  echo "Removing stale venv at '$VENV_ROOT'..."
  rm -rf "$VENV_ROOT"
  echo "Stale venv removed."
fi

echo "[TASK] Environment cleaned."

