# OWASP Top 10 Mapping

This document maps the application and delivery controls to the OWASP Top 10 (2021). It is an educational mapping, not a certification.

| Risk | Relevant controls | Evidence |
| --- | --- | --- |
| A01 Broken Access Control | Login-required dashboard, server-side `current_user` checks, safe `next` validation, separate RBAC role, default-deny NetworkPolicy | `app/secureapp/auth.py`, `app/secureapp/main.py`, `deploy/k8s/rbac.yaml`, `deploy/k8s/networkpolicy.yaml` |
| A02 Cryptographic Failures | scrypt password hashes, random secret generation outside tests, signed sessions, `HttpOnly`/`SameSite` cookies, conditional HSTS | `app/secureapp/models.py`, `app/secureapp/__init__.py`, `app/secureapp/security.py` |
| A03 Injection | SQLAlchemy query API, autoescaped Jinja templates, strict CSP, Bandit and Semgrep gates | `app/secureapp/auth.py`, `app/secureapp/templates/`, `security/`, CI `sast` job |
| A04 Insecure Design | Minimal authentication scope, generic login errors, rate limits, threat model, explicit documented limitations | `app/secureapp/auth.py`, `docs/THREAT_MODEL.md` |
| A05 Security Misconfiguration | Non-root UID 10001, read-only root filesystem, dropped capabilities, RuntimeDefault seccomp, restricted namespace, resource limits, security headers | `app/Dockerfile`, `deploy/k8s/`, CI `build-scan` |
| A06 Vulnerable and Outdated Components | Version-constrained requirements, pip-audit, Trivy image scan, Dependabot | `app/requirements*.txt`, `.github/workflows/ci.yml`, `.github/dependabot.yml` |
| A07 Identification and Authentication Failures | scrypt, generic failure message, login/register rate limits, strong session protection, logout invalidation | `app/secureapp/auth.py`, `app/secureapp/forms.py`, tests |
| A08 Software and Data Integrity Failures | Trusted CI build path, image tar checksums, CycloneDX SBOM, tagged release artifacts, SARIF results | `.github/workflows/ci.yml` |
| A09 Security Logging and Monitoring Failures | JSON audit events, login/rate-limit/access-denial counters, Prometheus ServiceMonitor, Grafana dashboard | `app/secureapp/telemetry.py`, `monitoring/` |
| A10 Server-Side Request Forgery | No user-controlled server-side URL fetching; app egress restricted to DNS | `deploy/k8s/networkpolicy.yaml` |

## Gaps

- No MFA, email verification, password reset, account lockout, or breached-password checking.
- No Web Application Firewall or DDoS protection.
- No independent penetration test; scanner results and automated tests are the current evidence.
- SARIF code scanning requires a public repository and appropriate GitHub permissions.
- The local HTTP demo intentionally sets `COOKIE_SECURE=false`; production use should terminate TLS and set it to `true`.
