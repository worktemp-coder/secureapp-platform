# Threat Model

## Assets

- User credentials and password hashes.
- Session cookies and the application signing secret.
- Application availability and the local SQLite database.
- CI credentials supplied by GitHub (`GITHUB_TOKEN`).
- Container image and release artifacts.

## Actors

- Anonymous internet or local-network user.
- Authenticated application user.
- Developer with repository write access.
- Compromised dependency or container base image.
- Attacker with access to the local Kubernetes host.

## Trust Boundaries

1. Browser to Flask/Gunicorn.
2. GitHub Actions runner to the repository and release artifacts.
3. kubelet/container runtime to the application container.
4. `secureapp` namespace to the monitoring and `kube-system` namespaces.
5. Local developer environment to the k3d cluster and generated secrets.

## Threats and Mitigations

| Threat | Mitigation | Residual risk |
| --- | --- | --- |
| Credential stuffing or password guessing | Login limit of 5 POSTs/minute by IP, generic failures, audit counters | No distributed limiter, account lockout, or MFA |
| Session theft | `HttpOnly`, `SameSite=Lax`, strong session protection, `Secure` when HTTPS is used | Local demo uses HTTP |
| Open redirect after login | Same-origin relative/same-host redirect validation; external, protocol-relative, and backslash targets rejected | URL parsing differences across clients remain possible |
| SQL injection | SQLAlchemy parameterized queries; no raw user input in SQL | Database compromise or application logic bugs |
| XSS | Jinja autoescaping and restrictive CSP | CSP allows only same-origin scripts/styles |
| CSRF | Flask-WTF CSRF on forms and logout | API endpoints are not in scope |
| Secret leakage | git-secrets in CI, gitignored local secret, GitHub-hosted token, no registry credentials | Developer could still paste a secret into an uncommitted file |
| Vulnerable dependency or base image | pip-audit, Trivy, Dependabot | No guaranteed zero-day coverage; base tag is not digest-pinned |
| Container breakout or privilege escalation | Non-root, read-only rootfs, dropped capabilities, no privilege escalation, RuntimeDefault seccomp | Shared kernel and local k3d runtime |
| Lateral movement | Default-deny ingress/egress, DNS-only egress, monitoring-only ingress on port 8000 | Port-forward bypasses NetworkPolicy by design |
| Data loss | PVC for SQLite, single replica | No replication, backup, or migration tooling |
| CI artifact tampering | GitHub-hosted runners, SARIF upload, SBOM/checksums in release | No cryptographic signing or provenance attestation |
| Observability data loss | Prometheus local storage with 6-hour retention | No long-term storage or Alertmanager |

## Out of Scope

TLS/Ingress, external identity federation, MFA, email delivery, payment data, multi-tenant isolation, persistent production CD, and a full backup/restore strategy.
