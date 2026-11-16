from urllib.parse import urlencode

from secureapp.extensions import db
from secureapp.models import User

PASSWORD = "correct-horse-battery-staple"


def register(client, username="alice", password=PASSWORD):
    return client.post(
        "/auth/register",
        data={
            "username": username,
            "password": password,
            "confirm_password": password,
        },
        follow_redirects=True,
    )


def login(client, username="alice", password=PASSWORD, next_url=None, **kwargs):
    path = "/auth/login"
    if next_url:
        path = f"{path}?{urlencode({'next': next_url})}"

    return client.post(
        path,
        data={"username": username, "password": password},
        **kwargs,
    )


def test_dashboard_requires_authentication(client):
    response = client.get("/dashboard")
    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_register_login_and_logout(client):
    response = register(client)
    assert response.status_code == 200
    assert b"Account created" in response.data

    response = login(client, follow_redirects=True)
    assert response.status_code == 200
    assert b"Welcome, alice" in response.data

    response = client.post("/auth/logout", follow_redirects=True)
    assert response.status_code == 200
    assert b"Signed out" in response.data

    response = client.get("/dashboard")
    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_login_failure_is_generic(client, create_user):
    create_user()
    response = login(client, password="this-is-the-wrong-password")
    assert response.status_code == 200
    assert b"Invalid username or password" in response.data
    assert b"Incorrect password" not in response.data


def test_open_redirect_is_blocked(client, create_user):
    create_user()
    response = login(
        client,
        next_url="https://evil.example/steal",
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert "evil.example" not in response.headers["Location"]
    assert response.headers["Location"].endswith("/dashboard")


def test_unsafe_next_url_variants_are_blocked(client, create_user):
    create_user()
    for candidate in ("//evil.example/steal", "/\\evil.example/steal"):
        response = login(
            client,
            next_url=candidate,
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert "evil.example" not in response.headers["Location"]
        assert response.headers["Location"].endswith("/dashboard")


def test_safe_next_url_is_allowed(client, create_user):
    create_user()
    response = login(
        client,
        next_url="/dashboard",
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/dashboard")


def test_password_is_hashed(app, create_user):
    create_user()
    with app.app_context():
        user = db.session.execute(
            db.select(User).where(User.username == "alice")
        ).scalar_one()
        assert user.password_hash != PASSWORD
        assert user.password_hash.startswith("scrypt:")
        assert user.check_password(PASSWORD)


def test_duplicate_username_is_rejected(client):
    register(client)
    response = register(client)
    assert response.status_code == 200
    assert b"Username is already taken" in response.data


def test_short_password_is_rejected(client):
    response = client.post(
        "/auth/register",
        data={
            "username": "alice",
            "password": "short",
            "confirm_password": "short",
        },
    )
    assert response.status_code == 200
    assert b"Field must be between 12 and 128 characters long" in response.data
