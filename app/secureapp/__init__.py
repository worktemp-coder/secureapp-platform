import logging
import os
import secrets

from flask import Flask
from pythonjsonlogger import json as jsonlogger

from .extensions import csrf, db, limiter, login_manager, metrics
from .security import register_security
from .telemetry import AUDIT_LOGGER


def _env_bool(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _configure_logging(level):
    root = logging.getLogger()
    if not root.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            jsonlogger.JsonFormatter(
                "%(asctime)s %(levelname)s %(name)s %(message)s",
                rename_fields={"asctime": "timestamp", "levelname": "level"},
            )
        )
        root.addHandler(handler)

    root.setLevel(level)
    AUDIT_LOGGER.setLevel(level)


@login_manager.user_loader
def load_user(user_id):
    from .models import User

    try:
        return db.session.get(User, int(user_id))
    except (TypeError, ValueError):
        return None


def create_app(test_config=None):
    app = Flask(__name__)

    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY") or secrets.token_hex(32),
        SQLALCHEMY_DATABASE_URI=os.environ.get("DATABASE_URL", "sqlite:///app.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=_env_bool("COOKIE_SECURE"),
        REMEMBER_COOKIE_HTTPONLY=True,
        REMEMBER_COOKIE_SECURE=_env_bool("COOKIE_SECURE"),
        WTF_CSRF_TIME_LIMIT=3600,
        RATELIMIT_STORAGE_URI=os.environ.get("RATELIMIT_STORAGE_URI", "memory://"),
        APP_ENV=os.environ.get("APP_ENV", "development"),
        LOG_LEVEL=os.environ.get("LOG_LEVEL", "INFO"),
        MAX_CONTENT_LENGTH=1024 * 1024,
    )

    if test_config:
        app.config.update(test_config)

    if (
        app.config["APP_ENV"] == "production"
        and not os.environ.get("SECRET_KEY")
        and not (test_config and "SECRET_KEY" in test_config)
    ):
        raise RuntimeError("SECRET_KEY must be set when APP_ENV=production")

    _configure_logging(app.config["LOG_LEVEL"].upper())

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    metrics.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please sign in to continue."
    login_manager.login_message_category = "info"
    login_manager.session_protection = "strong"

    from .auth import bp as auth_bp
    from .main import bp as main_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(main_bp)

    register_security(app)

    with app.app_context():
        from . import models  # noqa: F401

        db.create_all()

    return app
