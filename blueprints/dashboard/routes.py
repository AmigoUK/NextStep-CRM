from datetime import date

from flask import redirect, render_template, url_for

from blueprints.dashboard import dashboard_bp
from models import Client, Contact, FollowUp


@dashboard_bp.route("/")
def index():
    return redirect(url_for("dashboard.dashboard"))


@dashboard_bp.route("/dashboard")
def dashboard():
    today = date.today()

    # Stats
    active_clients = Client.query.filter(Client.status == "active").count()
    total_clients = Client.query.count()

    due_today = FollowUp.query.filter(
        FollowUp.due_date == today,
        FollowUp.completed == False,  # noqa: E712
    ).all()

    overdue = FollowUp.query.filter(
        FollowUp.due_date < today,
        FollowUp.completed == False,  # noqa: E712
    ).all()

    # Recent interactions (last 5)
    recent_contacts = (
        Contact.query
        .order_by(Contact.date.desc(), Contact.created_at.desc())
        .limit(5)
        .all()
    )

    return render_template(
        "dashboard/index.html",
        active_clients=active_clients,
        total_clients=total_clients,
        due_today=due_today,
        overdue=overdue,
        recent_contacts=recent_contacts,
    )
