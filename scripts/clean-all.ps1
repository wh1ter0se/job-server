param()
. "$PSScriptRoot/_common.ps1"

& (Join-Path $PSScriptRoot 'clean-environment.ps1')
& (Join-Path $PSScriptRoot 'clean-package.ps1')
