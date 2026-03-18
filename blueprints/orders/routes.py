from datetime import date
from functools import wraps

from flask import abort, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import func

from blueprints.orders import orders_bp
from extensions import db
from models import Company, Invoice, INVOICE_STATUSES, AppSettings
from blueprints.orders.invoice_csv import (
    generate_export_csv,
    generate_template_csv,
    validate_and_import,
)


def invoice_access_required(f):
    """Decorator: require login AND invoice access (accounts/manager/admin)."""
    @wraps(f)
    @login_required
    def wrapped(*args, **kwargs):
        if not current_user.can_access_invoices():
            abort(403)
        return f(*args, **kwargs)
    return wrapped


def _is_ajax():
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"


@orders_bp.route("/")
@invoice_access_required
def dashboard():
    """Invoice dashboard — summary cards, overdue alerts."""
    today = date.today()

    total_invoices = Invoice.query.count()
    total_outstanding = db.session.query(
        func.sum(Invoice.amount - func.coalesce(Invoice.paid_amount, 0))
    ).filter(Invoice.status.in_(["unpaid", "partially_paid"])).scalar() or 0

    overdue_count = Invoice.query.filter(
        Invoice.status.in_(["unpaid", "partially_paid"]),
        Invoice.due_date < today,
    ).count()

    overdue_amount = db.session.query(
        func.sum(Invoice.amount - func.coalesce(Invoice.paid_amount, 0))
    ).filter(
        Invoice.status.in_(["unpaid", "partially_paid"]),
        Invoice.due_date < today,
    ).scalar() or 0

    paid_count = Invoice.query.filter_by(status="paid").count()

    # Recent overdue invoices
    overdue_invoices = (
        Invoice.query
        .filter(Invoice.status.in_(["unpaid", "partially_paid"]), Invoice.due_date < today)
        .order_by(Invoice.due_date)
        .limit(10)
        .all()
    )

    return render_template(
        "accounts/dashboard.html",
        total_invoices=total_invoices,
        total_outstanding=round(total_outstanding, 2),
        overdue_count=overdue_count,
        overdue_amount=round(overdue_amount, 2),
        paid_count=paid_count,
        overdue_invoices=overdue_invoices,
    )


@orders_bp.route("/invoices")
@invoice_access_required
def invoice_list():
    """Invoice list — filterable, paginated."""
    q = request.args.get("q", "").strip()
    status_filter = request.args.get("status", "").strip()

    query = Invoice.query.join(Company)

    if q:
        query = query.filter(
            db.or_(
                Invoice.invoice_number.ilike(f"%{q}%"),
                Company.company_name.ilike(f"%{q}%"),
                Company.internal_id.ilike(f"%{q}%"),
            )
        )
    if status_filter:
        query = query.filter(Invoice.status == status_filter)

    settings = AppSettings.get()
    page = request.args.get("page", 1, type=int)
    ordered = query.order_by(Invoice.due_date.desc())

    if settings.pagination_enabled:
        pagination = ordered.paginate(page=page, per_page=settings.pagination_size, error_out=False)
        invoices = pagination.items
    else:
        pagination = None
        invoices = ordered.all()

    return render_template(
        "accounts/invoice_list.html",
        invoices=invoices,
        statuses=INVOICE_STATUSES,
        q=q,
        status=status_filter,
        pagination=pagination,
    )


@orders_bp.route("/invoices/<int:id>")
@invoice_access_required
def invoice_detail(id):
    invoice = db.get_or_404(Invoice, id)
    return render_template("accounts/invoice_detail.html", invoice=invoice)


@orders_bp.route("/invoices/<int:id>/edit", methods=["GET", "POST"])
@invoice_access_required
def edit_invoice(id):
    invoice = db.get_or_404(Invoice, id)

    if request.method == "POST":
        invoice.status = request.form.get("status", invoice.status)
        paid_date = request.form.get("paid_date", "").strip()
        if paid_date:
            from datetime import datetime
            try:
                invoice.paid_date = datetime.strptime(paid_date, "%Y-%m-%d").date()
            except ValueError:
                flash("Invalid paid date format.", "danger")
                return render_template("accounts/invoice_edit.html", invoice=invoice, statuses=INVOICE_STATUSES)
        else:
            invoice.paid_date = None

        paid_amount = request.form.get("paid_amount", "").strip()
        if paid_amount:
            try:
                invoice.paid_amount = float(paid_amount)
            except ValueError:
                flash("Invalid paid amount.", "danger")
                return render_template("accounts/invoice_edit.html", invoice=invoice, statuses=INVOICE_STATUSES)
        else:
            invoice.paid_amount = None

        invoice.notes = request.form.get("notes", "").strip()
        db.session.commit()
        flash(f"Invoice '{invoice.invoice_number}' updated.", "success")
        return redirect(url_for("accounts.invoice_detail", id=invoice.id))

    return render_template("accounts/invoice_edit.html", invoice=invoice, statuses=INVOICE_STATUSES)


@orders_bp.route("/import", methods=["GET", "POST"])
@invoice_access_required
def import_invoices():
    if request.method == "POST":
        file = request.files.get("file")
        if not file or not file.filename:
            flash("Please select a CSV file.", "danger")
            return render_template("accounts/invoice_import.html")

        upsert = "upsert" in request.form
        result = validate_and_import(file.stream, upsert=upsert)

        if result["errors"]:
            # Store errors in session for download
            from flask import session
            session["import_errors"] = result["errors"]

        flash(
            f"Import complete: {result['imported']} created, {result['updated']} updated, {result['skipped']} skipped.",
            "success" if not result["errors"] else "warning",
        )
        for w in result.get("warnings", []):
            flash(w, "warning")

        return render_template("accounts/invoice_import.html", result=result)

    return render_template("accounts/invoice_import.html")


@orders_bp.route("/export")
@invoice_access_required
def export_invoices():
    from flask import Response
    output = generate_export_csv()
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=invoices_export.csv"},
    )


@orders_bp.route("/template")
@invoice_access_required
def download_template():
    from flask import Response
    output = generate_template_csv()
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=invoices_template.csv"},
    )


@orders_bp.route("/analytics")
@invoice_access_required
def analytics():
    """Per-company payment performance table."""
    today = date.today()

    # Get all companies that have invoices
    companies_with_invoices = (
        db.session.query(
            Company.id,
            Company.company_name,
            Company.internal_id,
            func.count(Invoice.id).label("total_invoices"),
            func.sum(
                db.case(
                    (Invoice.status.in_(["unpaid", "partially_paid"]), Invoice.amount - func.coalesce(Invoice.paid_amount, 0)),
                    else_=0,
                )
            ).label("outstanding"),
            func.sum(
                db.case(
                    (
                        db.and_(
                            Invoice.status.in_(["unpaid", "partially_paid"]),
                            Invoice.due_date < today,
                        ),
                        1,
                    ),
                    else_=0,
                )
            ).label("overdue_count"),
            func.avg(Invoice.amount).label("avg_invoice_value"),
        )
        .join(Invoice, Company.id == Invoice.company_id)
        .group_by(Company.id)
        .order_by(Company.company_name)
        .all()
    )

    return render_template(
        "accounts/analytics.html",
        companies=companies_with_invoices,
    )
