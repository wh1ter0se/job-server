#!/usr/bin/env bash
set -e
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$script_dir/_common.sh"
cd "$workspace_root"

echo "[TASK] Cleaning package artifacts..."

build_dir="$workspace_root/build"
if [ -d "$build_dir" ]; then
  echo "Cleaning build folder at '$build_dir'..."
  rm -rf "$build_dir"
  echo "Build folder cleaned."
fi

dist_dir="$workspace_root/dist"
if [ -d "$dist_dir" ]; then
  echo "Cleaning dist folder at '$dist_dir'..."
  rm -rf "$dist_dir"
  echo "Dist folder cleaned."
fi

echo "[TASK] Package artifacts cleaned."
