#!/usr/bin/env bash
set -e
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$script_dir/_common.sh"
# cd "$workspace_root"

production=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    -p|--production)
      production=1
      shift
      ;;
    *)
      shift
      ;;
  esac
done

"$script_dir/clean-package.sh"
"$script_dir/generate-stubs.sh"

echo "[TASK] Building and installing package..."

if [ "$production" -eq 1 ]; then
  echo "Installing in production mode..."
  "$PYTHON_EXE" -m build --sdist --wheel --installer uv
  wheel=$(ls -t "$WORKSPACE_ROOT"/dist/*.whl | head -n1)
  uv pip install --python "$PYTHON_EXE" --force-reinstall "$wheel"
else
  echo "Installing in editable mode for debug..."
  uv pip install --python "$PYTHON_EXE" --force-reinstall --editable "$WORKSPACE_ROOT[test]"
fi

uv pip list --python "$PYTHON_EXE"

echo "[TASK] Package built and installed."
