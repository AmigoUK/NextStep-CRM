from flask import redirect, render_template, url_for

from blueprints.dashboard import dashboard_bp


@dashboard_bp.route("/")
def index():
    return redirect(url_for("dashboard.dashboard"))


@dashboard_bp.route("/dashboard")
def dashboard():
    return render_template("dashboard/index.html")
