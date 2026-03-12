from flask import flash, jsonify, redirect, render_template, request, url_for

from blueprints.settings import settings_bp
from extensions import db
from models import QuickFunction, CONTACT_TYPES, AppSettings


def _is_ajax():
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"


@settings_bp.route("/")
def settings_page():
    quick_functions = QuickFunction.query.order_by(
        QuickFunction.sort_order, QuickFunction.id
    ).all()
    settings = AppSettings.get()
    return render_template(
        "settings/index.html",
        quick_functions=quick_functions,
        contact_types=CONTACT_TYPES,
        settings=settings,
    )


@settings_bp.route("/quick-functions/new", methods=["POST"])
def create_quick_function():
    label = request.form.get("label", "").strip()
    if not label:
        flash("Label is required.", "danger")
        return redirect(url_for("settings.settings_page"))

    icon = request.form.get("icon", "bi-lightning-charge").strip()
    if not icon.startswith("bi-"):
        icon = "bi-" + icon

    max_order = db.session.query(db.func.max(QuickFunction.sort_order)).scalar() or 0

    qf = QuickFunction(
        label=label,
        icon=icon,
        contact_type=request.form.get("contact_type", "phone"),
        notes=request.form.get("notes", "").strip(),
        outcome=request.form.get("outcome", "").strip(),
        sort_order=max_order + 1,
    )
    db.session.add(qf)
    db.session.commit()
    flash(f"Quick function '{qf.label}' created.", "success")
    return redirect(url_for("settings.settings_page"))


@settings_bp.route("/quick-functions/<int:id>/edit", methods=["POST"])
def edit_quick_function(id):
    qf = db.get_or_404(QuickFunction, id)

    label = request.form.get("label", "").strip()
    if not label:
        flash("Label is required.", "danger")
        return redirect(url_for("settings.settings_page"))

    icon = request.form.get("icon", qf.icon).strip()
    if not icon.startswith("bi-"):
        icon = "bi-" + icon

    qf.label = label
    qf.icon = icon
    qf.contact_type = request.form.get("contact_type", qf.contact_type)
    qf.notes = request.form.get("notes", "").strip()
    qf.outcome = request.form.get("outcome", "").strip()
    db.session.commit()
    flash(f"Quick function '{qf.label}' updated.", "success")
    return redirect(url_for("settings.settings_page"))


@settings_bp.route("/quick-functions/<int:id>/toggle", methods=["POST"])
def toggle_quick_function(id):
    qf = db.get_or_404(QuickFunction, id)
    qf.is_active = not qf.is_active
    db.session.commit()

    state = "activated" if qf.is_active else "deactivated"
    if _is_ajax():
        return jsonify({"ok": True, "is_active": qf.is_active, "message": f"'{qf.label}' {state}."})

    flash(f"'{qf.label}' {state}.", "success")
    return redirect(url_for("settings.settings_page"))


@settings_bp.route("/quick-functions/<int:id>/delete", methods=["POST"])
def delete_quick_function(id):
    qf = db.get_or_404(QuickFunction, id)
    label = qf.label
    db.session.delete(qf)
    db.session.commit()
    flash(f"Quick function '{label}' deleted.", "success")
    return redirect(url_for("settings.settings_page"))


@settings_bp.route("/theme", methods=["POST"])
def update_theme():
    data = request.get_json(silent=True) or {}
    theme = data.get("theme", "light")
    if theme not in ("light", "dark", "auto"):
        return jsonify({"ok": False, "error": "Invalid theme."}), 400

    settings = AppSettings.get()
    settings.theme = theme
    db.session.commit()
    return jsonify({"ok": True, "theme": theme})
