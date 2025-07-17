# Common environment variables for scripts
# (source this at the top of every script)

# Determine repository root (parent of the scripts/ folder)
SCRIPT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Where the virtual environment lives
VENV_ROOT="${WORKSPACE_ROOT}/.venv"

# # # Pick the right executables on Windows vs *nix
if [ "$OS" = "Windows_NT" ]; then
    PYTHON_EXE="${VENV_ROOT}/Scripts/python.exe"
    STUBGEN_EXE="${VENV_ROOT}/Scripts/stubgen.exe"
else
    PYTHON_EXE="${VENV_ROOT}/bin/python"
    STUBGEN_EXE="${VENV_ROOT}/bin/stubgen"
fi

# PYTHON_EXE="${VENV_ROOT}/Scripts/python.exe"
# STUBGEN_EXE="${VENV_ROOT}/Scripts/stubgen.exe"

# if [ "$OS" = "Windows_NT" ]; then
#     ${VENV_ROOT}/Scripts/activate.bat
# else
#     ${VENV_ROOT}/Scripts/activate
# fi

# PYTHON_EXE="python3"
# STUBGEN_EXE="stubgen"