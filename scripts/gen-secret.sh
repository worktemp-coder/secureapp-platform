#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SECRET_FILE="$ROOT/deploy/k8s/secret.yaml"

if [[ -s "$SECRET_FILE" ]]; then
  echo "Using existing local secret file: $SECRET_FILE"
  exit 0
fi

if ! command -v openssl >/dev/null 2>&1; then
  echo "openssl is required to generate the application secret." >&2
  exit 1
fi

umask 077
SECRET_KEY="$(openssl rand -hex 32)"
cat >"$SECRET_FILE" <<EOF
apiVersion: v1
kind: Secret
metadata:
  name: secureapp-secrets
  namespace: secureapp
type: Opaque
stringData:
  SECRET_KEY: "$SECRET_KEY"
EOF
chmod 600 "$SECRET_FILE"

echo "Generated $SECRET_FILE (gitignored)."
