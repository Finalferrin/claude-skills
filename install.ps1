# Manual install for Claude Code, Codex, or both.
#   .\install.ps1 -Target Both
#
# Preferred route is the marketplace — see README.md:
#   /plugin marketplace add Finalferrin/claude-skills
#   /plugin install toolup@claude-skills

param(
    [ValidateSet("Claude", "Codex", "Both")]
    [string]$Target = "Both"
)

$ErrorActionPreference = "Stop"
$src  = Join-Path $PSScriptRoot "plugins"

$destinations = switch ($Target) {
    "Claude" { @(Join-Path $env:USERPROFILE ".claude\skills") }
    "Codex"  { @(Join-Path $env:USERPROFILE ".codex\skills") }
    "Both"   { @(
        (Join-Path $env:USERPROFILE ".claude\skills"),
        (Join-Path $env:USERPROFILE ".codex\skills")
    ) }
}

if (-not (Test-Path $src)) { throw "No plugins folder beside this script: $src" }

$count = 0
foreach ($dest in $destinations) {
    New-Item -ItemType Directory -Force -Path $dest | Out-Null
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
}

""
"$count skill installation(s) complete. Start a new Claude Code session or Codex task to refresh its skill catalog."
