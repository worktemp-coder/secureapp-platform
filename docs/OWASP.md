# OWASP Notes

I used the OWASP Top 10 (2021) as a checklist while building the app. This is not an audit or a certification.

| Risk | What I did | Where to look |
| --- | --- | --- |
| A01 Broken Access Control | Dashboard requires login; `current_user` checks are server-side; redirect target is validated; Kubernetes RBAC and default-deny network policy | `app/secureapp/auth.py`, `app/secureapp/main.py`, `deploy/k8s/rbac.yaml`, `deploy/k8s/networkpolicy.yaml` |
| A02 Cryptographic Failures | scrypt password hashes, random secret outside tests, signed sessions, HttpOnly/SameSite cookies, HSTS when HTTPS is used | `app/secureapp/models.py`, `app/secureapp/__init__.py`, `app/secureapp/security.py` |
| A03 Injection | SQLAlchemy queries, autoescaped Jinja templates, CSP, Bandit and Semgrep | `app/secureapp/auth.py`, `app/secureapp/templates/`, `security/`, CI `sast` job |
| A04 Insecure Design | Small auth scope, generic login errors, rate limits, written threat model, documented limits | `app/secureapp/auth.py`, `docs/THREAT_MODEL.md` |
| A05 Security Misconfiguration | Non-root user, read-only rootfs, dropped capabilities, RuntimeDefault seccomp, restricted namespace, resource limits, security headers | `app/Dockerfile`, `deploy/k8s/`, CI `build-scan` |
| A06 Vulnerable and Outdated Components | Constrained requirements, pip-audit, Trivy, Dependabot | `app/requirements*.txt`, `.github/workflows/ci.yml`, `.github/dependabot.yml` |
| A07 Identification and Authentication Failures | scrypt, generic failure message, login/register limits, strong session protection, logout | `app/secureapp/auth.py`, `app/secureapp/forms.py`, tests |
| A08 Software and Data Integrity Failures | CI-built image, checksums, CycloneDX SBOM, tagged release artifacts, SARIF results | `.github/workflows/ci.yml` |
| A09 Security Logging and Monitoring Failures | JSON audit events, login/rate-limit/access-denial counters, ServiceMonitor, Grafana dashboard | `app/secureapp/telemetry.py`, `monitoring/` |
| A10 Server-Side Request Forgery | No user-controlled server-side fetch; app egress is limited to DNS | `deploy/k8s/networkpolicy.yaml` |

## Where it falls short

- There is no MFA, email verification, password reset, account lockout, or breached-password check.
- There is no WAF or DDoS protection.
- No independent penetration test has been done. The evidence here is tests and scanner output.
- SARIF results need a public repository and the right GitHub permissions.
- The local demo runs over HTTP and sets `COOKIE_SECURE=false`. Anything exposed outside the laptop should use TLS.
