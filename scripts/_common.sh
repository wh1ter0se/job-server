#!/usr/bin/env bash
# Determine repo root (parent directory of this scripts folder)
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
workspace_root="$(cd "$script_dir/.." && pwd)"
venv_root="$workspace_root/.venv"

# Choose executables depending on platform
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
  python_exe="$venv_root/Scripts/python.exe"
  stubgen_exe="$venv_root/Scripts/stubgen.exe"
else
  python_exe="$venv_root/bin/python"
  stubgen_exe="$venv_root/bin/stubgen"
fi
