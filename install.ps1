# Manual install, for when the plugin marketplace is not an option.
#   powershell -NoProfile -File install.ps1
#
# Preferred route is the marketplace — see README.md:
#   /plugin marketplace add Finalferrin/claude-skills
#   /plugin install toolup@claude-skills

$ErrorActionPreference = "Stop"
$src  = Join-Path $PSScriptRoot "plugins"
$dest = Join-Path $env:USERPROFILE ".claude\skills"

if (-not (Test-Path $src)) { throw "No plugins folder beside this script: $src" }
New-Item -ItemType Directory -Force -Path $dest | Out-Null

$count = 0
Get-ChildItem $src -Directory | ForEach-Object {
    $skills = Join-Path $_.FullName "skills"
    if (Test-Path $skills) {
        Get-ChildItem $skills -Directory | ForEach-Object {
            Copy-Item $_.FullName $dest -Recurse -Force
            "installed {0,-20} -> {1}" -f $_.Name, (Join-Path $dest $_.Name)
            $count++
        }
    }
}

""
"$count skill(s) installed. Claude picks them up on the next session."
