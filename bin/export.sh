#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

# Export the contents of GraphDB repo "kieker" to a local Turtle dump.
# The dump is gitignored: collaborators supply their own copy.
OUT="data/kieker_dump.ttl"
TMP="$(mktemp data/.kieker_dump.XXXXXX)"
trap 'rm -f "$TMP"' EXIT

# infer=false because we use rdfs+ and don't want inference results in the dump
curl -fsS -H "Accept: text/turtle" \
  "http://localhost:7200/repositories/kieker/statements?infer=false" \
  > "$TMP"
mv "$TMP" "$OUT"

echo "Exported GraphDB repo 'kieker' -> $OUT"