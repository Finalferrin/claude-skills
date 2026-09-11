# Install these skills into your personal Claude skills directory.
#   powershell -NoProfile -File install.ps1

$ErrorActionPreference = "Stop"
$src  = Join-Path $PSScriptRoot "skills"
$dest = Join-Path $env:USERPROFILE ".claude\skills"

if (-not (Test-Path $src)) { throw "No skills folder beside this script: $src" }
New-Item -ItemType Directory -Force -Path $dest | Out-Null

Get-ChildItem $src -Directory | ForEach-Object {
    $target = Join-Path $dest $_.Name
    Copy-Item $_.FullName $dest -Recurse -Force
    "installed {0,-22} -> {1}" -f $_.Name, $target
}

""
"Done. Claude picks them up on the next session."
