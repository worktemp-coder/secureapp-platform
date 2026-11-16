def test_security_headers(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "frame-ancestors 'none'" in response.headers["Content-Security-Policy"]
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "no-referrer"
    assert response.headers["Permissions-Policy"] == (
        "camera=(), geolocation=(), microphone=()"
    )


def test_auth_pages_are_not_cached(client):
    response = client.get("/auth/login")
    assert response.headers["Cache-Control"] == "no-store"


def test_csrf_is_enforced_when_enabled(csrf_app):
    client = csrf_app.test_client()
    response = client.post(
        "/auth/login",
        data={"username": "alice", "password": "correct-horse-battery-staple"},
    )
    assert response.status_code == 400


def test_login_rate_limit(rate_limited_app):
    client = rate_limited_app.test_client()
    statuses = []
    for _ in range(6):
        response = client.post(
            "/auth/login",
            data={
                "username": "nobody",
                "password": "wrong-password-value",
            },
        )
        statuses.append(response.status_code)

    assert 429 in statuses


def test_rate_limit_metric_is_exported(rate_limited_app):
    client = rate_limited_app.test_client()
    for _ in range(6):
        client.post(
            "/auth/login",
            data={
                "username": "nobody",
                "password": "wrong-password-value",
            },
        )

    response = client.get("/metrics")
    assert response.status_code == 200
    assert b"secureapp_rate_limited_total" in response.data


def test_security_metrics_are_exported(client):
    client.post(
        "/auth/login",
        data={"username": "nobody", "password": "wrong-password-value"},
    )
    response = client.get("/metrics")
    assert response.status_code == 200
    assert b"secureapp_login_total" in response.data
    assert b'outcome="failure"' in response.data
