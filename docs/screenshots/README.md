# Screenshots

These images were captured from the local k3d demo and the GitHub Actions run. The commands behind them are in [../DEMO.md](../DEMO.md).

## Application

### Sign in

![SecureApp sign-in page](01-login.png)

### Signed-in dashboard

![SecureApp signed-in dashboard](02-authenticated-dashboard.png)

### Landing page

![SecureApp landing page after signing out](03-landing-page.png)

### Rate limit

![SecureApp 429 rate-limit page](06-rate-limit.png)

## Monitoring

### SecureApp Grafana dashboard

![Grafana SecureApp Security and SRE dashboard](04-grafana-overview.png)

### Prometheus SecureApp target

![Prometheus target for job secureapp marked UP](05-prometheus-secureapp-target.png)

### Prometheus overview

![Grafana Prometheus overview dashboard](11-prometheus-overview.png)

### All Prometheus targets

![Prometheus target health page](12-prometheus-targets.png)

### Grafana overview

![Grafana overview dashboard](13-grafana-stack.png)

## Kubernetes

### Pods, services, storage, policies, and accounts

![kubectl output for the secureapp namespace](07-kubectl-resources.png)

### Networking

![Grafana Kubernetes networking dashboard](14-kubernetes-networking.png)

### Kubelet

![Grafana Kubernetes kubelet dashboard](15-kubernetes-kubelet.png)

### Storage

![Grafana Kubernetes persistent volume dashboard](16-kubernetes-storage.png)

## GitHub Actions

### Successful CI run

![GitHub Actions CI run with all required jobs passing](08-actions-green.png)

The release job is skipped on `main`. It runs only for `v*` tags.

### Artifacts

![CI artifacts for the image, Bandit report, and pip-audit report](09-actions-artifacts.png)

### Pull request checks

![Pull request checks for Semgrep and Trivy](10-pr-checks.png)
