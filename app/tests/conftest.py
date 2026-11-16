import pytest
from secureapp import create_app
from secureapp.extensions import db, limiter
from secureapp.models import User


def _base_config(tmp_path, **overrides):
    config = {
        "TESTING": True,
        "SECRET_KEY": "test-secret-key",
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path / 'test.db'}",
        "WTF_CSRF_ENABLED": False,
        "RATELIMIT_ENABLED": False,
    }
    config.update(overrides)
    return config


@pytest.fixture()
def app(tmp_path):
    app = create_app(_base_config(tmp_path))
    yield app
    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.engine.dispose()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def csrf_app(tmp_path):
    app = create_app(_base_config(tmp_path, WTF_CSRF_ENABLED=True))
    yield app
    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.engine.dispose()


@pytest.fixture()
def rate_limited_app(tmp_path):
    app = create_app(_base_config(tmp_path, RATELIMIT_ENABLED=True))
    limiter.reset()
    yield app
    limiter.reset()
    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.engine.dispose()


@pytest.fixture()
def create_user(app):
    def _create(username="alice", password="correct-horse-battery-staple"):
        with app.app_context():
            user = User(username=username)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            return user.id

    return _create
