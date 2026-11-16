from datetime import UTC, datetime
from urllib.parse import urlsplit

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user

from .extensions import db, limiter
from .forms import LoginForm, RegisterForm
from .models import User
from .telemetry import LOGIN_COUNTER, audit

bp = Blueprint("auth", __name__)


def _is_safe_next_url(target):
    if not target or any(char in target for char in ("\\", "\r", "\n", "\t")):
        return False

    test = urlsplit(target)
    if test.scheme and test.scheme not in ("http", "https"):
        return False

    if test.netloc:
        return test.netloc.lower() == urlsplit(request.host_url).netloc.lower()

    return target.startswith("/") and not target.startswith("//")


@bp.route("/register", methods=["GET", "POST"])
@limiter.limit("3 per minute", methods=["POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data.strip().lower()
        existing = db.session.execute(
            db.select(User).where(User.username == username)
        ).scalar_one_or_none()

        if existing:
            form.username.errors.append("Username is already taken.")
            audit("register", "failure", username=username, reason="duplicate")
        else:
            user = User(username=username)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            audit("register", "success", username=username)
            flash("Account created. Please sign in.", "success")
            return redirect(url_for("auth.login"))
    elif form.is_submitted():
        audit(
            "register",
            "failure",
            username=(form.username.data or "")[:32],
            reason="validation",
        )

    return render_template("register.html", form=form)


@bp.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute", methods=["POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data.strip().lower()
        user = db.session.execute(
            db.select(User).where(User.username == username)
        ).scalar_one_or_none()

        if user and user.check_password(form.password.data):
            login_user(user)
            session.permanent = True
            user.last_login_at = datetime.now(UTC)
            db.session.commit()
            LOGIN_COUNTER.labels("success").inc()
            audit("login", "success", username=username)
            flash("Signed in successfully.", "success")

            next_url = request.args.get("next")
            if _is_safe_next_url(next_url):
                return redirect(next_url)
            return redirect(url_for("main.dashboard"))

        LOGIN_COUNTER.labels("failure").inc()
        audit("login", "failure", username=username, reason="invalid_credentials")
        flash("Invalid username or password.", "error")

    return render_template("login.html", form=form)


@bp.post("/logout")
@login_required
def logout():
    username = current_user.username
    logout_user()
    audit("logout", "success", username=username)
    flash("Signed out.", "info")
    return redirect(url_for("main.index"))
