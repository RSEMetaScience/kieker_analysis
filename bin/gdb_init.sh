#!/usr/bin/env sh
set -eu

REPO_ID="${REPO_ID:-kieker}"
GRAPHDB_URL="${GRAPHDB_URL:-http://graphdb:7200}"
CONFIG_PATH="${CONFIG_PATH:-/data/config.ttl}"
DATA_PATH="${DATA_PATH:-/data/kieker.trig}"

# if set to 1, delete + recreate repo and re-import TTL
FORCE_REINIT="${FORCE_REINIT:-0}"

# Stored in persisted volume (graphdb/home), so it survives restarts
INIT_MARKER="${INIT_MARKER:-/opt/graphdb/home/.init-${REPO_ID}.done}"

echo "Waiting for GraphDB at ${GRAPHDB_URL}..."
for i in $(seq 1 60); do
  if curl -fsS "${GRAPHDB_URL}/rest/repositories" >/dev/null; then
    break
  fi
  sleep 1
done

repo_exists() {
  curl -fsS "${GRAPHDB_URL}/rest/repositories/${REPO_ID}" >/dev/null 2>&1
}

# normally we won't overwrite user data on restart
if [ "${FORCE_REINIT}" != "1" ]; then
  if [ -f "${INIT_MARKER}" ]; then
    echo "Init marker present (${INIT_MARKER}). Skipping init."
    exit 0
  fi
  if repo_exists; then
    echo "Repository '${REPO_ID}' already exists. Writing marker and skipping seed import."
    touch "${INIT_MARKER}"
    exit 0
  fi
fi
# if we made it here then we are deleting and rebuilding the repository using our saved turtle data and config
echo "Recreating repository (${REPO_ID})..."
curl -fsS -X DELETE "${GRAPHDB_URL}/rest/repositories/${REPO_ID}" >/dev/null || true

curl -fsS -X POST "${GRAPHDB_URL}/rest/repositories" \
  -H "Content-Type: multipart/form-data" \
  -F "config=@${CONFIG_PATH}" >/dev/null

echo "Loading RDF triples from ${DATA_PATH}..."
curl -fsS -X POST \
  -H "Content-Type: text/turtle" \
  --data-binary "@${DATA_PATH}" \
  "${GRAPHDB_URL}/repositories/${REPO_ID}/statements" >/dev/null

touch "${INIT_MARKER}"
echo "Init complete: repo=${REPO_ID}"