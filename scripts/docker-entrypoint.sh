#!/bin/sh
set -eu

STORAGE_DIR="${FORMAFORGE_STORAGE_DIR:-/data/bronze}"
mkdir -p "${STORAGE_DIR}"

if [ -z "${ANTHROPIC_API_KEY:-}" ]; then
  echo "warning: ANTHROPIC_API_KEY is not set; AI-assisted Silver conversion will fail." >&2
fi

exec "$@"
