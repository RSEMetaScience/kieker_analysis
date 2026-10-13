#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")/.."

# Start GraphDB if needed
docker compose up -d graphdb

# Force re-init from committed turtle/config
docker compose run --rm -e FORCE_REINIT=1 graphdb-init