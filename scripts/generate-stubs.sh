#!/usr/bin/env bash
set -e
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$script_dir/_common.sh"

echo "[TASK] Generating stubs..."

stubs_dir="$WORKSPACE_ROOT/src/jobserver/stubs"
if [ -d "$stubs_dir" ]; then
  echo "Removing old stubs at '$stubs_dir'..."
  rm -rf "$stubs_dir"
  echo "Old stubs removed."
fi

echo "Generating new stubs at '$stubs_dir'..."
echo "$STUBGEN_EXE" --no-import -o "$stubs_dir" "$WORKSPACE_ROOT/src/jobserver" 2>&1
"$STUBGEN_EXE" --no-import -o "$stubs_dir" "$WORKSPACE_ROOT/src/jobserver" 2>&1
echo "New stubs generated."

echo "[TASK] Stubs generated."
