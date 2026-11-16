# Academic Evaluation Notes

## Project Summary

SecureApp Platform is a third-year B.Tech portfolio project that integrates secure application development with a DevSecOps delivery workflow and Kubernetes observability. It is intentionally scoped for a single laptop but covers a representative end-to-end path from source code to a running, monitored workload.

## Implemented Outcomes

| Outcome | Evidence |
| --- | --- |
| Secure authentication | scrypt hashes, CSRF, generic failures, safe redirects, session protection |
| Abuse resistance | 5/minute login and 3/minute registration limits, 429 handling |
| Secure HTTP behavior | CSP, frame denial, nosniff, referrer and permissions policies, conditional HSTS |
| Automated quality gate | 18 pytest tests, 92.95% coverage, Ruff clean |
| Supply-chain checks | git-secrets, Semgrep, Bandit, pip-audit, Trivy, SBOM, Dependabot |
| Container hardening | Multi-stage build, non-root UID 10001, read-only runtime, health check |
| Kubernetes hardening | Restricted namespace, no service-account token, RBAC, default-deny NetworkPolicy, resource limits |
| Delivery automation | GitHub Actions build, scan, artifact, release, and k3d smoke deployment |
| Observability | JSON audit logs, Prometheus counters, ServiceMonitor, 9-panel Grafana dashboard |
| Documentation | OWASP mapping, threat model, runbook, demo script, GitHub setup |

## Verification Results

- Host test run: Python 3.14.4, 18 passed, 92.95% statement coverage.
- `ruff check app`: no findings.
- Container build: verified locally with Docker 29.1.3 using a refreshed Python 3.12 slim base.
- Container smoke: `/healthz`, `/readyz`, login page, security headers, and `/metrics` returned expected results with a read-only root filesystem.
- Image hardening: runtime pip/setuptools metadata removed; Trivy reports 0 HIGH/CRITICAL vulnerabilities after base-package upgrades.
- k3d deployment: verified on 2026-11-16 with a running pod, bound PVC, successful registration/login, and a persisted SQLite file.
- Monitoring: kube-prometheus-stack 93.3.0 installed; Grafana 13.3.1 healthy; `SecureApp Security and SRE` dashboard loaded with 9 panels; Prometheus reports the secureapp target as UP and scrapes `flask_http_request_total` and `secureapp_login_total`.
- Local gates: Semgrep 0 findings, Bandit 0 findings on Python 3.12, pip-audit clean, git-secrets clean.
- GitHub Actions: record the first green run and code-scanning evidence after pushing.

## Design Decisions

- **Flask over a larger framework:** keeps the security behavior explicit and reviewable for an academic demonstration.
- **SQLite:** avoids an external database while still exercising a persistent volume and readiness check. It limits the app to one replica.
- **In-memory rate limiter:** requires no Redis, but limits are per process rather than cluster-wide.
- **No registry:** image tarballs and GitHub Releases keep the project self-contained and avoid credential management.
- **No Terraform:** the assessment focus is application and container security. Kubernetes manifests are still linted and smoke-deployed.
- **Port-forward instead of Ingress:** avoids TLS and DNS complexity while keeping the demo reproducible.
- **Trivy plus pip-audit:** provides dependency and image visibility without an NVD API key.

## Scope Boundaries

This is not a production identity platform. It does not implement MFA, password reset, email verification, account lockout, external OIDC, a WAF, distributed rate limiting, database migrations, high availability, backup/restore, Alertmanager, Loki, or long-term metric storage. The README and threat model state these limits explicitly.

## Possible Viva Questions

1. **Why scrypt instead of SHA-256?** scrypt is memory-hard and slows offline guessing; a plain hash is unsuitable for passwords.
2. **Why validate `next` instead of redirecting to it directly?** Unvalidated redirects enable phishing and token leakage.
3. **Why read-only root filesystems?** They limit post-compromise persistence and accidental runtime modification.
4. **Why both NetworkPolicy and RBAC?** They control different planes: network reachability and Kubernetes API authorization.
5. **Why is the app still single-replica?** SQLite and the `Recreate` strategy prioritize simplicity; horizontal scaling would require an external database and shared limiter.
6. **What does the SBOM prove?** It lists the components in the image, enabling downstream vulnerability and license review.
7. **What is not covered by the CI scan?** Runtime behavior, business-logic flaws, secrets introduced after the scan, and zero-day vulnerabilities.

## Future Work

- External OIDC provider with MFA and account recovery.
- PostgreSQL and migration-based schema management.
- Redis-backed distributed rate limiting.
- Registry push with digest pinning, image signing, and provenance attestation.
- Ingress with TLS, WAF, and HSTS preload.
- Alertmanager and persistent Prometheus storage.
- Backup and restore test for the application database.
