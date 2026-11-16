#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLUSTER="${CLUSTER:-secureapp}"
IMAGE="${IMAGE:-secureapp:dev}"

"$ROOT/scripts/cluster-up.sh"

kubectl apply -f "$ROOT/deploy/k8s/namespace.yaml"

if ! kubectl -n secureapp get secret secureapp-secrets >/dev/null 2>&1; then
  "$ROOT/scripts/gen-secret.sh"
  kubectl apply -f "$ROOT/deploy/k8s/secret.yaml"
else
  echo "Secret 'secureapp-secrets' already exists; leaving it unchanged."
fi

echo "Building $IMAGE..."
docker build --pull -t "$IMAGE" "$ROOT/app"

echo "Importing $IMAGE into k3d cluster '$CLUSTER'..."
k3d image import -c "$CLUSTER" "$IMAGE"

kubectl apply -k "$ROOT/deploy/k8s"
kubectl -n secureapp rollout status deployment/secureapp --timeout=180s

kubectl -n secureapp get pods,svc,pvc
echo
echo "Application: http://127.0.0.1:8080"
echo "Start port-forward: kubectl -n secureapp port-forward svc/secureapp 8080:80"
