# common.ps1 — define $workspaceRoot, $venvRoot, $pythonExe and $stubgenExe
# (dot-source this at the top of every script)

# Determine your repo root (parent of the scripts/ folder)
$workspaceRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path

# Where the venv lives
$venvRoot = Join-Path $workspaceRoot '.venv'

# Pick the right executables on Windows vs *nix
$IsWindows = $PSVersionTable.PSEdition -eq 'Desktop' -or $PSVersionTable.Platform -eq 'Win32NT'
if ($IsWindows) {
    $pythonExe = Join-Path $venvRoot 'Scripts\python.exe'
    $stubgenExe = Join-Path $venvRoot 'Scripts\stubgen.exe'
} else {
    $pythonExe = Join-Path $venvRoot 'bin/python'
    $stubgenExe = Join-Path $venvRoot 'bin/stubgen'
}
