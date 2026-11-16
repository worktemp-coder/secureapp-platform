from flask import Blueprint, jsonify, redirect, render_template, url_for
from flask_login import current_user, login_required
from sqlalchemy import text

from .extensions import db

bp = Blueprint("main", __name__)


@bp.get("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    return render_template("index.html")


@bp.get("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", user=current_user)


@bp.get("/healthz")
def healthz():
    return jsonify(status="ok"), 200


@bp.get("/readyz")
def readyz():
    try:
        db.session.execute(text("SELECT 1"))
    except Exception:
        return jsonify(status="not-ready"), 503
    return jsonify(status="ready"), 200
