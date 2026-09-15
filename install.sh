#!/usr/bin/env bash
# Manual install for Claude Code, Codex, or both.
#   bash install.sh --target both
#
# Preferred route is the marketplace — see README.md:
#   /plugin marketplace add Finalferrin/claude-skills
#   /plugin install toolup@claude-skills
set -euo pipefail

target="both"
if [ "$#" -gt 0 ]; then
  [ "$#" -eq 2 ] && [ "$1" = "--target" ] || {
    echo "Usage: $0 [--target claude|codex|both]" >&2
    exit 2
  }
  target="$2"
fi

case "$target" in
  claude) destinations=("${HOME}/.claude/skills") ;;
  codex) destinations=("${HOME}/.codex/skills") ;;
  both) destinations=("${HOME}/.claude/skills" "${HOME}/.codex/skills") ;;
  *) echo "Target must be claude, codex, or both." >&2; exit 2 ;;
esac

src="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/plugins"

[ -d "$src" ] || { echo "No plugins folder beside this script: $src" >&2; exit 1; }

count=0
for dest in "${destinations[@]}"; do
  mkdir -p "$dest"
  for plugin in "$src"/*/; do
    [ -d "${plugin}skills" ] || continue
    for skill in "${plugin}skills"/*/; do
      name="$(basename "$skill")"
      cp -r "$skill" "$dest/"
      printf 'installed %-20s -> %s\n' "$name" "$dest/$name"
      count=$((count+1))
    done
  done
done

echo
echo "$count skill installation(s) complete. Start a new Claude Code session or Codex task to refresh its skill catalog."
