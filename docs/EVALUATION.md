# Evaluation Notes

## What this is

SecureApp combines a small Flask application with the checks and deployment steps I wanted to learn: dependency scanning, container scanning, Kubernetes hardening, and basic observability. The scope stays on one laptop. It is not a production template, and the limitations are listed at the end.

## What works

| Area | Result |
| --- | --- |
| Authentication | scrypt hashes, CSRF, generic failures, safe redirects, session protection |
| Abuse handling | 5 login POSTs/minute and 3 registration POSTs/minute, with a 429 page |
| HTTP headers | CSP, frame denial, nosniff, referrer and permissions policies, conditional HSTS |
| Tests | 18 pytest tests, 92.95% coverage, Ruff clean |
| Supply chain | git-secrets, Semgrep, Bandit, pip-audit, Trivy, SBOM, Dependabot |
| Container | Non-root UID 10001, read-only rootfs, health check, no pip in the runtime image |
| Kubernetes | Restricted namespace, no service-account token, RBAC, default-deny NetworkPolicy, resource limits |
| Delivery | GitHub Actions build, scan, artifact upload, release, and k3d smoke deployment |
| Monitoring | JSON audit logs, Prometheus counters, ServiceMonitor, 9-panel Grafana dashboard |

## Results

- Tests: Python 3.14.4, 18 passed, 92.95% statement coverage.
- Ruff: no findings.
- Container: built with Docker 29.1.3 and tested with a read-only root filesystem.
- Container checks: `/healthz`, `/readyz`, login page, security headers, and `/metrics` behaved as expected.
- Image scan: Trivy reported 0 HIGH or CRITICAL vulnerabilities after updating the base packages and removing pip/setuptools from the runtime image.
- k3d: pod running, PVC bound, registration and login worked, and SQLite data survived the pod restart.
- Monitoring: kube-prometheus-stack 93.3.0 installed; Grafana 13.3.1 healthy; the `SecureApp Security and SRE` dashboard has 9 panels; the `secureapp` target is UP.
- Local gates: Semgrep and Bandit found nothing; pip-audit and git-secrets were clean.
- GitHub Actions: the workflow is green on `main`. Code-scanning results need a signed-in GitHub session to view.

## Choices I made

- **Flask instead of a larger framework.** The security code is easy to read and discuss.
- **SQLite.** It avoids an external database but still exercises a persistent volume and readiness check. It also limits the app to one replica.
- **In-memory rate limiting.** No Redis is needed, but limits are per worker and reset with the process.
- **No registry.** The demo imports the image into k3d directly. Releases attach an image tarball instead.
- **No Terraform.** The focus is application, container, and Kubernetes security. The manifests are still rendered and smoke-tested.
- **Port-forwarding.** It avoids DNS and TLS setup for a local demo.
- **Trivy with pip-audit.** It covers both the image and Python dependencies without needing an NVD API key.

## Not included

There is no MFA, email verification, password reset, account lockout, OIDC, WAF, distributed rate limiter, database migration system, high availability, backup automation, Alertmanager, Loki, or long-term metric storage. TLS and ingress are also out of scope.

## Design questions

1. **Why scrypt?** It is memory-hard, so offline guessing is slower than with a plain hash such as SHA-256.
2. **Why check the `next` parameter?** Passing it straight to `redirect()` creates an open redirect and can leak credentials to another site.
3. **Why a read-only root filesystem?** It gives an attacker fewer places to write after a compromise.
4. **Why RBAC and NetworkPolicy?** RBAC controls Kubernetes API access; NetworkPolicy controls network traffic. They solve different problems.
5. **Why only one app replica?** SQLite and the in-memory limiter would not behave correctly across replicas.
6. **What does the SBOM give you?** A component list that can be checked for vulnerabilities and licences later.
7. **What does CI not catch?** Business-logic mistakes, runtime behavior, secrets added after a scan, and new vulnerabilities without a database entry.

## Next steps

- Add an external identity provider with MFA and account recovery.
- Move to PostgreSQL and a migration tool.
- Use Redis for shared rate limits.
- Push to a registry, sign the image, and add provenance.
- Add TLS, an ingress controller, Alertmanager, and persistent Prometheus storage.
- Write and test a database backup and restore process.
