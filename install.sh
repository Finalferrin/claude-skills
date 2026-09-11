#!/usr/bin/env bash
# Install these skills into your personal Claude skills directory.
#   bash install.sh
set -euo pipefail

src="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/skills"
dest="${HOME}/.claude/skills"

[ -d "$src" ] || { echo "No skills folder beside this script: $src" >&2; exit 1; }
mkdir -p "$dest"

for d in "$src"/*/; do
  name="$(basename "$d")"
  cp -r "$d" "$dest/"
  printf 'installed %-22s -> %s\n' "$name" "$dest/$name"
done

echo
echo "Done. Claude picks them up on the next session."
