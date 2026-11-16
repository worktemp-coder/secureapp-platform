#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if command -v git-secrets >/dev/null 2>&1; then
  git secrets --scan
fi

PATTERN='-----BEGIN (RSA|OPENSSH|EC|DSA) PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}'
if grep -RInE \
  --exclude-dir=.git \
  --exclude-dir=.venv \
  --exclude-dir=.helm-cache \
  --exclude-dir=__pycache__ \
  --exclude='git-secrets-patterns.txt' \
  -- "$PATTERN" .; then
  echo "Potential secret material found." >&2
  exit 1
fi

echo "Secret scan passed."
