#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CHART_VERSION="${CHART_VERSION:-93.3.0}"
RELEASE="${RELEASE:-monitoring}"
NAMESPACE="${NAMESPACE:-monitoring}"
CHART_DIR="${CHART_DIR:-$ROOT/.helm-cache}"
CHART_PACKAGE="${CHART_PACKAGE:-$CHART_DIR/kube-prometheus-stack-$CHART_VERSION.tgz}"

"$ROOT/scripts/cluster-up.sh"

kubectl get namespace "$NAMESPACE" >/dev/null 2>&1 || kubectl create namespace "$NAMESPACE"

if ! kubectl -n "$NAMESPACE" get secret grafana-admin >/dev/null 2>&1; then
  GRAFANA_PASSWORD="$(openssl rand -hex 16)"
  kubectl -n "$NAMESPACE" create secret generic grafana-admin \
    --from-literal=admin-user=admin \
    --from-literal=admin-password="$GRAFANA_PASSWORD" >/dev/null
  echo "Grafana admin user: admin"
  echo "Grafana admin password: $GRAFANA_PASSWORD"
else
  echo "Grafana admin secret already exists; leaving it unchanged."
fi

if [[ ! -s "$CHART_PACKAGE" ]]; then
  mkdir -p "$CHART_DIR"
  for attempt in 1 2 3; do
    echo "Downloading kube-prometheus-stack $CHART_VERSION (attempt $attempt/3)..."
    if helm pull kube-prometheus-stack \
      --repo https://prometheus-community.github.io/helm-charts \
      --version "$CHART_VERSION" \
      --destination "$CHART_DIR"; then
      break
    fi
    sleep 10
  done
fi

if [[ ! -s "$CHART_PACKAGE" ]]; then
  echo "Unable to obtain chart package: $CHART_PACKAGE" >&2
  exit 1
fi

echo "Installing kube-prometheus-stack $CHART_VERSION..."
helm upgrade --install "$RELEASE" "$CHART_PACKAGE" \
  --namespace "$NAMESPACE" \
  -f "$ROOT/monitoring/values/kube-prometheus-stack-lowmem.yaml" \
  --wait \
  --atomic \
  --timeout 15m

kubectl apply -f "$ROOT/monitoring/dashboards/secureapp-dashboard.yaml"
kubectl apply -f "$ROOT/monitoring/servicemonitor.yaml"

echo
echo "Grafana: http://127.0.0.1:3000"
echo "  kubectl -n $NAMESPACE port-forward svc/monitoring-grafana 3000:80"
echo "Prometheus: http://127.0.0.1:9090"
echo "  kubectl -n $NAMESPACE port-forward svc/monitoring-kube-prometheus-prometheus 9090:9090"
echo "Grafana password:"
echo "  kubectl -n $NAMESPACE get secret grafana-admin -o jsonpath='{.data.admin-password}' | base64 -d"
