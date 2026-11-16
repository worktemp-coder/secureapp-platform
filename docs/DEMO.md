# Demo and Screenshot List

The demo takes about 10 to 15 minutes. Use passing runs and clean terminal output for screenshots.

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

Screenshot: `docs/screenshots/03-kubectl-resources.png`.

## 3. Show login and metrics

1. Open <http://127.0.0.1:8080>.
2. Capture the sign-in page as `01-login.png`.
3. Create a demo account, for example `demo_user`, with a password of at least 12 characters.
4. Try a wrong password six times to hit the 429 limit.
5. Wait a minute, then sign in.
6. Capture the signed-in dashboard as `02-authenticated-dashboard.png`.

Optional checks:

```bash
curl -fsS http://127.0.0.1:8080/healthz
curl -fsS http://127.0.0.1:8080/readyz
curl -fsS http://127.0.0.1:8080/metrics | grep -E 'secureapp_login_total|secureapp_rate_limited_total'
```

## 4. Show Grafana

1. Open <http://127.0.0.1:3000> and sign in as `admin`.
2. Open **Dashboards > SecureApp Security and SRE**.
3. Set the time range to **Last 30 minutes** and refresh every 10 seconds.
4. Capture the top row as `04-grafana-overview.png`.
5. Scroll to failed logins, login outcomes, and rate-limited requests. Capture them as `05-grafana-security.png`.
6. Open **Status > Targets** in Prometheus and check that the `secureapp` target is UP.

## 5. Show GitHub evidence

After the workflow is green on `main`:

1. Open **Actions > CI** and capture the successful run as `06-actions-green.png`.
2. Open **Security > Code scanning** and capture the results as `07-code-scanning.png`.
3. Open the run's **Artifacts** section and capture it as `08-artifacts.png`.
4. Open a pull request and capture the green checks as `09-pr-checks.png`.
5. Push a `v*` tag, wait for the release job, and capture the release assets as `10-release.png`.
6. Open **Settings > Branches** and capture the protected `main` rule as `11-branch-protection.png`.

Do not include terminal output or screenshots that contain secrets or tokens.
