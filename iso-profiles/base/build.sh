#!/usr/bin/env bash
#
# build.sh — thin wrapper -> ../../build-iso.sh base
# Kept for backwards compatibility; use build-iso.sh directly.
#
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/../../build-iso.sh" base "$@"
