import os
import uuid

from flask import current_app, flash, jsonify, redirect, request, send_from_directory, url_for
from werkzeug.utils import secure_filename

from blueprints.attachments import attachments_bp
from extensions import db
from models import Attachment


def _is_ajax():
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"


def _save_file(file, client_id):
    """Save uploaded file to disk and return (stored_filename, file_size, mime_type)."""
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    client_dir = os.path.join(upload_folder, str(client_id))
    os.makedirs(client_dir, exist_ok=True)

    original_name = secure_filename(file.filename)
    if not original_name:
        original_name = "unnamed_file"
    stored_name = f"{uuid.uuid4().hex}_{original_name}"
    file_path = os.path.join(client_dir, stored_name)
    file.save(file_path)

    file_size = os.path.getsize(file_path)
    mime_type = file.content_type or ""

    return stored_name, file_size, mime_type, original_name


@attachments_bp.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")
    client_id = request.form.get("client_id")

    if not file or not file.filename:
        flash("No file selected.", "danger")
        return redirect(request.referrer or url_for("dashboard.dashboard"))

    if not client_id:
        flash("Client is required.", "danger")
        return redirect(request.referrer or url_for("dashboard.dashboard"))

    client_id = int(client_id)
    contact_id = request.form.get("contact_id")
    followup_id = request.form.get("followup_id")

    stored_name, file_size, mime_type, original_name = _save_file(file, client_id)

    attachment = Attachment(
        filename=original_name,
        stored_filename=stored_name,
        file_size=file_size,
        mime_type=mime_type,
        client_id=client_id,
        contact_id=int(contact_id) if contact_id else None,
        followup_id=int(followup_id) if followup_id else None,
    )
    db.session.add(attachment)
    db.session.commit()

    if _is_ajax():
        return jsonify({
            "ok": True,
            "message": f"File '{original_name}' uploaded successfully.",
        })

    flash(f"File '{original_name}' uploaded successfully.", "success")
    return redirect(request.referrer or url_for("clients.detail_client", id=client_id))


@attachments_bp.route("/<int:id>/download")
def download(id):
    attachment = db.get_or_404(Attachment, id)
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    client_dir = os.path.join(upload_folder, str(attachment.client_id))
    return send_from_directory(
        client_dir,
        attachment.stored_filename,
        download_name=attachment.filename,
        as_attachment=True,
    )


@attachments_bp.route("/<int:id>/delete", methods=["POST"])
def delete(id):
    attachment = db.get_or_404(Attachment, id)
    client_id = attachment.client_id
    filename = attachment.filename

    # Delete file from disk
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    file_path = os.path.join(upload_folder, str(client_id), attachment.stored_filename)
    if os.path.exists(file_path):
        os.remove(file_path)

    db.session.delete(attachment)
    db.session.commit()

    if _is_ajax():
        return jsonify({"ok": True, "message": f"File '{filename}' deleted."})

    flash(f"File '{filename}' deleted.", "success")
    return redirect(request.referrer or url_for("clients.detail_client", id=client_id))
