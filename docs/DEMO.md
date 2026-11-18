# Demo and Screenshot List

The demo takes about 10 to 15 minutes. The screenshots already in `docs/screenshots/` were captured from this flow. If you repeat the demo, use a passing CI run and clean terminal output.

## 1. Start the local stack

```bash
make deploy
make monitoring
```

Open three terminals:

```bash
# Terminal 1
kubectl -n secureapp port-forward svc/secureapp 8080:80

# Terminal 2
kubectl -n monitoring port-forward svc/monitoring-grafana 3000:80

# Terminal 3
kubectl -n monitoring port-forward svc/monitoring-kube-prometheus-prometheus 9090:9090
```

## 2. Show the Kubernetes resources

```bash
kubectl -n secureapp get pods,svc,pvc,networkpolicy,serviceaccount
kubectl -n secureapp get deployment secureapp -o yaml | grep -E 'runAsNonRoot|readOnlyRootFilesystem|allowPrivilegeEscalation|automountServiceAccountToken'
```

Screenshot: `docs/screenshots/07-kubectl-resources.png`.

## 3. Show login and rate limiting

1. Open <http://127.0.0.1:8080>.
2. Capture the sign-in page as `01-login.png`.
3. Create an account, for example `demo_user1`, with a password of at least 12 characters.
4. Sign in and capture the dashboard as `02-authenticated-dashboard.png`.
5. Sign out and capture the landing page as `03-landing-page.png`.
6. Try a wrong password six times and capture the 429 page as `06-rate-limit.png`.
7. Wait a minute, then sign in again.

Optional checks:

```bash
curl -fsS http://127.0.0.1:8080/healthz
curl -fsS http://127.0.0.1:8080/readyz
curl -fsS http://127.0.0.1:8080/metrics | grep -E 'secureapp_login_total|secureapp_rate_limited_total'
```

## 4. Show Grafana and Prometheus

1. Open <http://127.0.0.1:3000> and sign in as `admin`.
2. Open **Dashboards > SecureApp Security and SRE**.
3. Set the time range to **Last 30 minutes** and refresh every 10 seconds.
4. Capture the top of the dashboard as `04-grafana-overview.png`.
5. Open **Status > Targets** in Prometheus, filter for `secureapp`, and capture the UP target as `05-prometheus-secureapp-target.png`.

Supporting screenshots are in the gallery:

- `11-prometheus-overview.png`
- `12-prometheus-targets.png`
- `13-grafana-stack.png`
- `14-kubernetes-networking.png`
- `15-kubernetes-kubelet.png`
- `16-kubernetes-storage.png`

## 5. Show GitHub evidence

After the workflow is green on `main`:

1. Open **Actions > CI** and capture the successful run as `08-actions-green.png`. The release job is skipped on `main` and only runs for tags.
2. Open the run's **Artifacts** section and capture `09-actions-artifacts.png`.
3. Open a pull request and capture the checks as `10-pr-checks.png`.

Do not include terminal output or screenshots that contain secrets or tokens.
