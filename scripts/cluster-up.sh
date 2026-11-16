#!/usr/bin/env bash
set -euo pipefail

CLUSTER="${CLUSTER:-secureapp}"

if ! command -v k3d >/dev/null 2>&1; then
  echo "k3d is required: https://k3d.io" >&2
  exit 1
fi

if k3d cluster list -o json 2>/dev/null | jq -e --arg name "$CLUSTER" '.[] | select(.name == $name)' >/dev/null; then
  if [[ "$(k3d cluster list -o json | jq -r --arg name "$CLUSTER" '.[] | select(.name == $name) | .serversRunning')" == "0" ]]; then
    echo "Starting stopped k3d cluster '$CLUSTER'..."
    k3d cluster start "$CLUSTER" --wait
  else
    echo "k3d cluster '$CLUSTER' is already running."
  fi
else
  echo "Creating k3d cluster '$CLUSTER'..."
  k3d cluster create "$CLUSTER" \
    --servers 1 \
    --agents 0 \
    --wait \
    --k3s-arg "--disable=traefik@server:0" \
    --k3s-arg "--disable=servicelb@server:0" \
    --k3s-arg "--disable=metrics-server@server:0"
fi

kubectl config use-context "k3d-$CLUSTER" >/dev/null
kubectl wait --for=condition=Ready node --all --timeout=120s
echo "Cluster ready: k3d-$CLUSTER"
