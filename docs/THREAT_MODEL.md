# Threat Model

This is a small app, so the threat model is small. I focused on the things that change when an app is put in a container and a cluster: credentials, the image, Kubernetes permissions, and network access.

## Assets

- User credentials and password hashes.
- Session cookies and the app signing secret.
- The local SQLite database and application availability.
- The CI token supplied by GitHub.
- The container image and release artifacts.

## Actors

- An anonymous user on the local machine or network.
- A signed-in user.
- A developer with write access to the repository.
- A compromised dependency or base image.
- Someone with access to the local Kubernetes host.

## Trust boundaries

1. Browser to Flask/Gunicorn.
2. GitHub Actions runner to the repository and release artifacts.
3. kubelet/container runtime to the app container.
4. `secureapp` namespace to `monitoring` and `kube-system`.
5. Local development environment to the k3d cluster and generated secrets.

## Threats and mitigations

| Threat | Mitigation | What is left |
| --- | --- | --- |
| Password guessing or credential stuffing | 5 POSTs/minute by IP, generic failures, audit counters | No shared rate limiter, account lockout, or MFA |
| Session theft | HttpOnly, SameSite=Lax, strong session protection, Secure cookies when HTTPS is used | The local demo uses HTTP |
| Open redirect after login | Same-origin relative or same-host targets only; external, protocol-relative, and backslash targets rejected | URL parsing differs between clients |
| SQL injection | SQLAlchemy parameterised queries; no user input in raw SQL | Database compromise and logic bugs |
| XSS | Jinja autoescaping and a restrictive CSP | Same-origin scripts and styles are allowed |
| CSRF | Flask-WTF protection on forms and logout | JSON or API endpoints are not in scope |
| Secret leakage | git-secrets in CI, gitignored local secret, GitHub-hosted token, no registry credentials | A secret can still be pasted into an uncommitted file |
| Vulnerable dependency or base image | pip-audit, Trivy, Dependabot | New vulnerabilities can appear between scans |
| Container escape or privilege escalation | Non-root user, read-only rootfs, dropped capabilities, no privilege escalation, RuntimeDefault seccomp | The local k3d runtime shares the host kernel |
| Lateral movement | Default-deny ingress and egress, DNS-only egress, monitoring-only ingress on port 8000 | Port-forward bypasses NetworkPolicy by design |
| Data loss | PVC for SQLite, single replica | No replication or backup |
| CI artifact tampering | GitHub-hosted runners, SARIF upload, SBOM and checksums | No signing or provenance attestation |
| Monitoring data loss | Six-hour Prometheus retention | No long-term storage or Alertmanager |

## Out of scope

TLS and ingress, external identity federation, MFA, email delivery, payment data, multi-tenant isolation, production deployment, and a full backup/restore plan.
