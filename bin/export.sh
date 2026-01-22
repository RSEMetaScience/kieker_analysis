#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

# Export current contents of repo "kieker" back to the committed Turtle file
curl -fsS -H "Accept: text/turtle" \
  "http://localhost:7200/repositories/kieker/statements" \
  > data/kieker.ttl

echo "Exported GraphDB repo 'kieker' -> data/kieker.ttl"