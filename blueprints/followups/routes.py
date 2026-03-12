import os
import uuid
from datetime import date, datetime, timedelta

from flask import current_app, flash, jsonify, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

from blueprints.followups import followups_bp
from extensions import db
from models import Client, FollowUp, PRIORITIES, Attachment


def _is_ajax():
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"


@followups_bp.route("/")
def list_followups():
    priority = request.args.get("priority", "").strip()
    show_overdue = request.args.get("overdue", "").strip()
    show_completed = request.args.get("completed", "").strip()

    query = FollowUp.query.join(Client)

    if priority:
        query = query.filter(FollowUp.priority == priority)
    if show_overdue == "1":
        query = query.filter(
            FollowUp.completed == False,  # noqa: E712
            FollowUp.due_date < date.today(),
        )
    if show_completed == "1":
        query = query.filter(FollowUp.completed == True)  # noqa: E712
    elif show_completed == "0":
        query = query.filter(FollowUp.completed == False)  # noqa: E712

    followups = query.order_by(FollowUp.due_date).all()
    return render_template(
        "followups/list.html",
        followups=followups,
        priorities=PRIORITIES,
        selected_priority=priority,
        show_overdue=show_overdue,
        show_completed=show_completed,
    )


@followups_bp.route("/new", methods=["GET", "POST"])
def create_followup():
    if request.method == "POST":
        client_id = request.form.get("client_id")
        due_date_str = request.form.get("due_date", "").strip()
        priority = request.form.get("priority", "medium")

        if not client_id:
            if _is_ajax():
                clients = Client.query.order_by(Client.company_name).all()
                html = render_template(
                    "followups/_form_fields.html",
                    followup=None,
                    clients=clients,
                    priorities=PRIORITIES,
                    selected_client_id=None,
                    today=date.today().isoformat(),
                    panel_mode=True,
                )
                return jsonify({"ok": False, "html": html})
            flash("Please select a client.", "danger")
            return redirect(url_for("followups.create_followup"))

        try:
            parsed_date = datetime.strptime(due_date_str, "%Y-%m-%d").date() if due_date_str else date.today()
        except ValueError:
            parsed_date = date.today()

        due_time_str = request.form.get("due_time", "").strip()
        parsed_time = None
        if due_time_str:
            try:
                parsed_time = datetime.strptime(due_time_str, "%H:%M").time()
            except ValueError:
                pass

        followup = FollowUp(
            client_id=int(client_id),
            due_date=parsed_date,
            due_time=parsed_time,
            priority=priority,
            notes=request.form.get("notes", "").strip(),
        )
        db.session.add(followup)
        db.session.flush()

        # Handle optional file attachment
        file = request.files.get("file")
        if file and file.filename:
            _save_followup_file(file, int(client_id), followup.id)

        db.session.commit()

        if _is_ajax():
            return jsonify({
                "ok": True,
                "message": "Follow-up created successfully.",
                "redirect": url_for("clients.detail_client", id=followup.client_id),
            })

        flash("Follow-up created successfully.", "success")
        return redirect(url_for("clients.detail_client", id=followup.client_id))

    client_id = request.args.get("client_id")
    clients = Client.query.order_by(Client.company_name).all()

    if _is_ajax():
        return render_template(
            "followups/_form_fields.html",
            followup=None,
            clients=clients,
            priorities=PRIORITIES,
            selected_client_id=int(client_id) if client_id else None,
            today=date.today().isoformat(),
            panel_mode=True,
        )

    return render_template(
        "followups/form.html",
        followup=None,
        clients=clients,
        priorities=PRIORITIES,
        selected_client_id=int(client_id) if client_id else None,
        today=date.today().isoformat(),
    )


@followups_bp.route("/<int:id>/edit", methods=["GET", "POST"])
def edit_followup(id):
    followup = db.get_or_404(FollowUp, id)

    if request.method == "POST":
        client_id = request.form.get("client_id")
        due_date_str = request.form.get("due_date", "").strip()

        if not client_id:
            flash("Please select a client.", "danger")
            clients = Client.query.order_by(Client.company_name).all()
            return render_template(
                "followups/form.html",
                followup=followup,
                clients=clients,
                priorities=PRIORITIES,
                selected_client_id=followup.client_id,
                today=date.today().isoformat(),
            )

        try:
            followup.due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date() if due_date_str else date.today()
        except ValueError:
            followup.due_date = date.today()

        due_time_str = request.form.get("due_time", "").strip()
        if due_time_str:
            try:
                followup.due_time = datetime.strptime(due_time_str, "%H:%M").time()
            except ValueError:
                followup.due_time = None
        else:
            followup.due_time = None

        followup.client_id = int(client_id)
        followup.priority = request.form.get("priority", "medium")
        followup.notes = request.form.get("notes", "").strip()
        followup.completed = "completed" in request.form

        # Handle optional file attachment
        file = request.files.get("file")
        if file and file.filename:
            _save_followup_file(file, int(client_id), followup.id)

        db.session.commit()
        flash("Follow-up updated successfully.", "success")
        return redirect(url_for("clients.detail_client", id=followup.client_id))

    clients = Client.query.order_by(Client.company_name).all()
    return render_template(
        "followups/form.html",
        followup=followup,
        clients=clients,
        priorities=PRIORITIES,
        selected_client_id=followup.client_id,
        today=date.today().isoformat(),
    )


@followups_bp.route("/<int:id>/complete", methods=["POST"])
def complete_followup(id):
    followup = db.get_or_404(FollowUp, id)
    followup.completed = not followup.completed
    db.session.commit()
    status = "completed" if followup.completed else "reopened"

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({
            "status": status,
            "completed": followup.completed,
            "clientId": followup.client_id,
            "clientName": followup.client.company_name,
            "notes": followup.notes or "",
        })

    flash(f"Follow-up marked as {status}.", "success")
    return redirect(request.referrer or url_for("followups.list_followups"))


@followups_bp.route("/matrix")
def matrix():
    today = date.today()
    tomorrow = today + timedelta(days=1)
    show_completed = request.args.get("show_completed", "0").strip()

    query = FollowUp.query.join(Client)
    if show_completed != "1":
        query = query.filter(FollowUp.completed == False)  # noqa: E712

    followups = query.order_by(FollowUp.due_date).all()

    do_first, schedule, delegate, eliminate = [], [], [], []
    for fu in followups:
        is_urgent = fu.due_date <= tomorrow
        is_important = fu.priority == "high"
        if is_urgent and is_important:
            do_first.append(fu)
        elif not is_urgent and is_important:
            schedule.append(fu)
        elif is_urgent and not is_important:
            delegate.append(fu)
        else:
            eliminate.append(fu)

    return render_template(
        "followups/matrix.html",
        do_first=do_first,
        schedule=schedule,
        delegate=delegate,
        eliminate=eliminate,
        show_completed=show_completed,
    )


def _save_followup_file(file, client_id, followup_id):
    """Save an uploaded file and create an Attachment record for a follow-up."""
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    client_dir = os.path.join(upload_folder, str(client_id))
    os.makedirs(client_dir, exist_ok=True)

    original_name = secure_filename(file.filename) or "unnamed_file"
    stored_name = f"{uuid.uuid4().hex}_{original_name}"
    file_path = os.path.join(client_dir, stored_name)
    file.save(file_path)

    attachment = Attachment(
        filename=original_name,
        stored_filename=stored_name,
        file_size=os.path.getsize(file_path),
        mime_type=file.content_type or "",
        client_id=client_id,
        followup_id=followup_id,
    )
    db.session.add(attachment)


@followups_bp.route("/<int:id>/delete", methods=["POST"])
def delete_followup(id):
    followup = db.get_or_404(FollowUp, id)
    client_id = followup.client_id
    db.session.delete(followup)
    db.session.commit()
    flash("Follow-up deleted successfully.", "success")
    return redirect(url_for("clients.detail_client", id=client_id))
