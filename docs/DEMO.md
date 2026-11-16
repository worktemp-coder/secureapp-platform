# Demo and Screenshot Checklist

The demo should take 10-15 minutes. Capture only green/successful results.

## 1. Start the Local Platform

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

## 2. Capture Kubernetes Evidence

```bash
kubectl -n secureapp get pods,svc,pvc,networkpolicy,serviceaccount
kubectl -n secureapp get deployment secureapp -o yaml | grep -E 'runAsNonRoot|readOnlyRootFilesystem|allowPrivilegeEscalation|automountServiceAccountToken'
```

Screenshot: `docs/screenshots/03-kubectl-resources.png`.

## 3. Demonstrate Authentication and Metrics

1. Open <http://127.0.0.1:8080>.
2. Capture the sign-in page: `01-login.png`.
3. Create a demo account, for example `demo_user` with a 12+ character password.
4. Attempt an incorrect password six times to trigger the 429 rate limit.
5. Wait one minute, then sign in successfully.
6. Capture the authenticated dashboard: `02-authenticated-dashboard.png`.

Optional verification:

```bash
curl -fsS http://127.0.0.1:8080/healthz
curl -fsS http://127.0.0.1:8080/readyz
curl -fsS http://127.0.0.1:8080/metrics | grep -E 'secureapp_login_total|secureapp_rate_limited_total'
```

## 4. Capture Grafana Evidence

1. Open <http://127.0.0.1:3000> and sign in as `admin`.
2. Open **Dashboards > SecureApp Security and SRE**.
3. Set the time range to **Last 30 minutes** and refresh to 10 seconds.
4. Capture the top row: `04-grafana-overview.png`.
5. Scroll to failed logins, login outcomes, and rate-limited requests: `05-grafana-security.png`.
6. Optionally open **Status > Targets** in Prometheus and confirm the secureapp ServiceMonitor is UP.

## 5. Capture GitHub Actions Evidence

After the first push to `main`:

1. Open **Actions > CI** and capture the successful run with all jobs: `06-actions-green.png`.
2. Open **Security > Code scanning** and show the query results: `07-code-scanning.png`.
3. Open the completed run's **Artifacts** section: `08-artifacts.png`.
4. Open a pull request from a feature branch and capture the green required checks: `09-pr-checks.png`.
5. Create and push a `v*` tag, wait for the release job, and capture the GitHub Release assets: `10-release.png`.
6. Open **Settings > Branches** and capture the protected `main` rule and required checks: `11-branch-protection.png`.

Do not capture red runs, failed attempts, or terminal output containing secrets or tokens.
