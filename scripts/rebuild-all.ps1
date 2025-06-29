param()
. "$PSScriptRoot/_common.ps1"

echo "[TASK] Starting full rebuild..."

& (Join-Path $PSScriptRoot 'setup-environment.ps1')
& (Join-Path $PSScriptRoot 'rebuild-install-package.ps1')

echo "[TASK] Full rebuild complete."