#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")/.."

BUILD=0
for arg in "$@"; do
  case "$arg" in
    --build) BUILD=1 ;;
    -h|--help)
      echo "Usage: bin/run [--build]"
      echo "  --build   Recreate GraphDB repo from TTL (runs graphdb-init with FORCE_REINIT=1)"
      exit 0
      ;;
    *)
      echo "Unknown argument: $arg" >&2
      exit 2
      ;;
  esac
done

graphdb_up() {
  # True if GraphDB responds
  curl -fsS "http://localhost:7200/rest/repositories" >/dev/null 2>&1
}

start_graphdb_if_needed() {
  if graphdb_up; then
    echo "GraphDB already running."
    return 0
  fi

  echo "Starting GraphDB..."
  docker compose up -d graphdb

  echo "Waiting for GraphDB..."
  for _ in $(seq 1 60); do
    if graphdb_up; then
      echo "GraphDB is up."
      return 0
    fi
    sleep 1
  done

  echo "GraphDB did not start in time." >&2
  exit 1
}

rebuild_db() {
  echo "Rebuilding GraphDB repo from TTL..."
  FORCE_REINIT=1 docker compose up -d graphdb-init
  docker compose logs -n 200 graphdb-init
}

jupyter_running() {
  # run the jupyter lab list command and send any errors down a black hole
  # pipe the output to grep with extended regex (-E) urls in the output means jupter is running)
  # -q silence grep to justr return 0 on match, 1 if not
  poetry run jupyter lab list 2>/dev/null | grep -qE '^http(s)?://'
}

start_jupyter() {
  echo "Installing Python deps if needed (poetry)..."
  poetry install

  if jupyter_running; then
    echo "JupyterLab already running:"
    poetry run jupyter lab list || true
    echo "Not starting a second instance."
    return 0
  fi

  echo "Starting JupyterLab..."
  exec poetry run jupyter lab
}

start_graphdb_if_needed

if [ "$BUILD" -eq 1 ]; then
  rebuild_db
fi

start_jupyter