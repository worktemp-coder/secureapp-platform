# Runbook

## Deploy or update

```bash
make deploy
```

This starts the k3d cluster if it is stopped, creates the app secret if the cluster does not have one, builds `secureapp:dev`, imports it, applies the manifests, and waits for the rollout.

## Check it

```bash
kubectl -n secureapp get pods,svc,pvc,networkpolicy,serviceaccount
kubectl -n secureapp rollout status deployment/secureapp
kubectl -n secureapp port-forward svc/secureapp 8080:80
curl -fsS http://127.0.0.1:8080/healthz
curl -fsS http://127.0.0.1:8080/readyz
curl -fsS http://127.0.0.1:8080/metrics | grep secureapp_login_total
```

`/healthz` only checks the process. `/readyz` checks that the database answers a query.

## Logs and events

```bash
kubectl -n secureapp logs deployment/secureapp --tail=100
kubectl -n secureapp logs deployment/secureapp -f
kubectl -n secureapp get events --sort-by=.lastTimestamp | tail -20
```

Logs are JSON. Audit entries use `event=login`, `event=rate_limit`, and `outcome=failure`.

## Roll back

```bash
kubectl -n secureapp rollout history deployment/secureapp
kubectl -n secureapp rollout undo deployment/secureapp
```

The Deployment uses `Recreate` and one replica, so expect a short outage during a rollout or rollback.

## Rotate secrets

The app secret signs sessions. Changing it signs everyone out.

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
kubectl -n monitoring rollout restart deployment/monitoring-grafana
kubectl -n monitoring rollout status deployment/monitoring-grafana
```

`scripts/deploy-monitoring.sh` creates a new password only if the secret is missing. It prints the new password once.

## Monitoring

```bash
make monitoring
kubectl -n monitoring get pods
kubectl -n monitoring port-forward svc/monitoring-grafana 3000:80
kubectl -n monitoring port-forward svc/monitoring-kube-prometheus-prometheus 9090:9090
```

In Prometheus, open **Status > Targets** and check that `secureapp` is UP. The job label is `secureapp`. Grafana loads `SecureApp Security and SRE` from the labelled ConfigMap.

## When something breaks

| Symptom | Check | Fix |
| --- | --- | --- |
| `CreateContainerConfigError` | `kubectl -n secureapp describe pod` | Make sure secret `secureapp-secrets` exists and has `SECRET_KEY` |
| `ErrImageNeverPull` or `ImagePullBackOff` | `kubectl -n secureapp describe pod` | Run `make deploy` again and check that `k3d image import` worked |
| PVC stays `Pending` | `kubectl -n secureapp get pvc`, `kubectl get storageclass` | Check that the k3d `local-path` storage class exists |
| App runs but `/readyz` returns 503 | Pod logs | Check the `/data` mount and that the app can write `sqlite:////data/app.db` |
| Login returns 429 | Expected rate limit | Wait a minute. The limit is 5 login POSTs and 3 registration POSTs per minute |
| Grafana dashboard is empty | Grafana sidecar logs and Prometheus targets | Check the `grafana_dashboard: "1"` label and the ServiceMonitor |
| Prometheus target is DOWN | NetworkPolicy, service port, namespace labels | Monitoring must be in namespace `monitoring`; the scrape port is `8000` |
| `make monitoring` cannot download the chart | Network access to the Prometheus chart repository | Retry. The script caches chart 93.3.0 in `.helm-cache/` after the first download |

## Clean up

```bash
make cluster-down
```

This deletes the k3d cluster and its storage. The generated `deploy/k8s/secret.yaml` stays on disk; delete it too if you are done with the project.
