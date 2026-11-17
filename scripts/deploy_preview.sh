#!/usr/bin/env bash
# Example preview deploy hook for deploy_shell executor
set -euo pipefail
INITIATIVE_ID="${1:-unknown}"
echo "[tdt-deploy] dry-run preview for ${INITIATIVE_ID}"
echo "[tdt-deploy] would build, push tag, and hit smoke endpoint"
