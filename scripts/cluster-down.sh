#!/usr/bin/env bash
set -euo pipefail

CLUSTER="${CLUSTER:-secureapp}"

if command -v k3d >/dev/null 2>&1; then
  k3d cluster delete "$CLUSTER"
else
  echo "k3d is not installed." >&2
  exit 1
fi
