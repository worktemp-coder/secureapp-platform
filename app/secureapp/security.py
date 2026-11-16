from flask import render_template, request

from .telemetry import ACCESS_DENIED_COUNTER, RATE_LIMIT_COUNTER, audit

CONTENT_SECURITY_POLICY = (
    "default-src 'self'; "
    "base-uri 'self'; "
    "form-action 'self'; "
    "frame-ancestors 'none'; "
    "img-src 'self' data:; "
    "style-src 'self'; "
    "script-src 'self'"
)


def register_security(app):
    @app.after_request
    def set_security_headers(response):
        response.headers["Content-Security-Policy"] = CONTENT_SECURITY_POLICY
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = (
            "camera=(), geolocation=(), microphone=()"
        )
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        response.headers["Cross-Origin-Resource-Policy"] = "same-origin"

        if request.is_secure:
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )

        if request.path.startswith(("/auth", "/dashboard")):
            response.headers["Cache-Control"] = "no-store"

        return response

    @app.errorhandler(403)
    def forbidden(_error):
        ACCESS_DENIED_COUNTER.labels("forbidden").inc()
        audit("access", "denied", reason="forbidden")
        return render_template("error.html", code=403, message="Access denied."), 403

    @app.errorhandler(404)
    def not_found(_error):
        return (
            render_template("error.html", code=404, message="Page not found."),
            404,
        )

    @app.errorhandler(429)
    def rate_limited(_error):
        RATE_LIMIT_COUNTER.inc()
        audit("rate_limit", "blocked", reason="too_many_requests")
        return (
            render_template(
                "error.html",
                code=429,
                message="Too many attempts. Try again in a minute.",
            ),
            429,
        )

    @app.errorhandler(500)
    def server_error(_error):
        return (
            render_template(
                "error.html",
                code=500,
                message="Something went wrong.",
            ),
            500,
        )
