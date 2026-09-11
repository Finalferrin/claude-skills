#!/usr/bin/env bash
# Manual install, for when the plugin marketplace is not an option.
#   bash install.sh
#
# Preferred route is the marketplace — see README.md:
#   /plugin marketplace add Finalferrin/claude-skills
#   /plugin install toolup@claude-skills
set -euo pipefail

src="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/plugins"
dest="${HOME}/.claude/skills"

[ -d "$src" ] || { echo "No plugins folder beside this script: $src" >&2; exit 1; }
mkdir -p "$dest"

count=0
for plugin in "$src"/*/; do
  [ -d "${plugin}skills" ] || continue
  for skill in "${plugin}skills"/*/; do
    name="$(basename "$skill")"
    cp -r "$skill" "$dest/"
    printf 'installed %-20s -> %s\n' "$name" "$dest/$name"
    count=$((count+1))
  done
done

echo
echo "$count skill(s) installed. Claude picks them up on the next session."
