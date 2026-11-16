# Runbook

## Deploy or Update

```bash
make deploy
```

This creates the k3d cluster if needed, generates the app secret if the cluster secret does not exist, builds `secureapp:dev`, imports it into k3d, applies the Kustomize manifests, and waits for the rollout.

## Verify

```bash
kubectl -n secureapp get pods,svc,pvc,networkpolicy,serviceaccount
kubectl -n secureapp rollout status deployment/secureapp
kubectl -n secureapp port-forward svc/secureapp 8080:80
curl -fsS http://127.0.0.1:8080/healthz
curl -fsS http://127.0.0.1:8080/readyz
curl -fsS http://127.0.0.1:8080/metrics | grep secureapp_login_total
```

`/healthz` proves the process is up. `/readyz` checks the database connection.

## Logs and Events

```bash
kubectl -n secureapp logs deployment/secureapp --tail=100
kubectl -n secureapp logs deployment/secureapp -f
kubectl -n secureapp get events --sort-by=.lastTimestamp | tail -20
```

Application and audit logs are JSON. Look for `event=login`, `event=rate_limit`, and `outcome=failure`.

## Rollback

```bash
kubectl -n secureapp rollout history deployment/secureapp
kubectl -n secureapp rollout undo deployment/secureapp
```

Because the Deployment uses `Recreate` and a single replica, a brief outage is expected during rollout or rollback.

## Secret Rotation

The application secret signs sessions; rotating it invalidates all sessions.

```bash
rm -f deploy/k8s/secret.yaml
scripts/gen-secret.sh
kubectl apply -f deploy/k8s/secret.yaml
kubectl -n secureapp rollout restart deployment/secureapp
kubectl -n secureapp rollout status deployment/secureapp
```

For Grafana:

```bash
kubectl -n monitoring delete secret grafana-admin
scripts/deploy-monitoring.sh
```

## Monitoring

```bash
make monitoring
kubectl -n monitoring get pods
kubectl -n monitoring port-forward svc/monitoring-grafana 3000:80
kubectl -n monitoring port-forward svc/monitoring-kube-prometheus-prometheus 9090:9090
```

Check the Prometheus target:

1. Open Prometheus at <http://127.0.0.1:9090>.
2. Go to **Status > Targets**.
3. Confirm the `secureapp` target is `UP` (job label `secureapp`).

Grafana loads `SecureApp Security and SRE` from the labeled ConfigMap.

## Common Failures

| Symptom | Check | Action |
| --- | --- | --- |
| Pod `CreateContainerConfigError` | `kubectl -n secureapp describe pod` | Ensure secret `secureapp-secrets` exists and has `SECRET_KEY` |
| `ErrImageNeverPull` or `ImagePullBackOff` | `kubectl -n secureapp describe pod` | Re-run `make deploy`; confirm `k3d image import -c secureapp secureapp:dev` succeeded |
| PVC `Pending` | `kubectl -n secureapp get pvc`, `kubectl get storageclass` | Confirm k3d's default `local-path` StorageClass is available |
| App starts but `/readyz` is 503 | Pod logs | Check PVC mount and writable `/data`; the app uses `sqlite:////data/app.db` |
| 429 during demo | Expected rate-limit response | Wait one minute; limits are 5 login POSTs and 3 registration POSTs per minute per client |
| Grafana dashboard is empty | Grafana sidecar logs and Prometheus targets | Confirm the ConfigMap label `grafana_dashboard: "1"` and the ServiceMonitor namespace/labels |
| Prometheus target is DOWN | NetworkPolicy, service port, or namespace labels | Monitoring namespace must be named `monitoring`; scrape port is `8000` |
| `make monitoring` fails on chart download | Network access to the Prometheus community repository | Retry; the script caches the pinned `93.3.0` package under `.helm-cache/` |

## Cleanup

```bash
make cluster-down
```

This deletes the k3d cluster and its local storage. The generated `deploy/k8s/secret.yaml` file remains gitignored; remove it manually if rotating or decommissioning.
