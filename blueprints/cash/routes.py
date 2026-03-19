from datetime import date
from functools import wraps

from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import func

from blueprints.cash import cash_bp
from extensions import db
from models import AppSettings, Company
from models.cash_transaction import CashTransaction


def cash_access_required(f):
    """Decorator: require login, cash module enabled, and appropriate role."""
    @wraps(f)
    @login_required
    def wrapped(*args, **kwargs):
        settings = AppSettings.get()
        if not settings.cash_module_enabled:
            abort(404)
        return f(*args, **kwargs)
    return wrapped


def _get_transactions_query():
    """Return base query filtered by user role."""
    q = CashTransaction.query
    if not current_user.has_role_at_least("manager"):
        q = q.filter_by(user_id=current_user.id)
    return q


@cash_bp.route("/")
@cash_access_required
def dashboard():
    """Cash dashboard — per-user summary."""
    q = _get_transactions_query()

    total_in = db.session.query(func.coalesce(func.sum(CashTransaction.amount), 0)).filter(
        CashTransaction.id.in_(q.filter_by(type="in").with_entities(CashTransaction.id))
    ).scalar()

    total_out = db.session.query(func.coalesce(func.sum(CashTransaction.amount), 0)).filter(
        CashTransaction.id.in_(q.filter_by(type="out").with_entities(CashTransaction.id))
    ).scalar()

    net = total_in - total_out

    recent = q.order_by(CashTransaction.transaction_date.desc(), CashTransaction.id.desc()).limit(10).all()

    # Per-company summary
    company_ids = db.session.query(CashTransaction.company_id).filter(
        CashTransaction.id.in_(q.with_entities(CashTransaction.id))
    ).distinct().all()
    company_ids = [c[0] for c in company_ids]

    company_summaries = []
    for cid in company_ids:
        company = db.session.get(Company, cid)
        if not company:
            continue
        c_in = db.session.query(func.coalesce(func.sum(CashTransaction.amount), 0)).filter(
            CashTransaction.id.in_(q.filter_by(type="in", company_id=cid).with_entities(CashTransaction.id))
        ).scalar()
        c_out = db.session.query(func.coalesce(func.sum(CashTransaction.amount), 0)).filter(
            CashTransaction.id.in_(q.filter_by(type="out", company_id=cid).with_entities(CashTransaction.id))
        ).scalar()
        company_summaries.append({
            "company": company,
            "cash_in": c_in,
            "cash_out": c_out,
            "net": c_in - c_out,
        })

    company_summaries.sort(key=lambda x: abs(x["net"]), reverse=True)

    return render_template("cash/dashboard.html",
                           total_in=total_in, total_out=total_out, net=net,
                           recent=recent, company_summaries=company_summaries)


@cash_bp.route("/transactions")
@cash_access_required
def transaction_list():
    """Full transaction list with filters."""
    q = _get_transactions_query()

    # Filters
    company_id = request.args.get("company_id", type=int)
    tx_type = request.args.get("type", "")
    date_from = request.args.get("date_from", "")
    date_to = request.args.get("date_to", "")

    if company_id:
        q = q.filter_by(company_id=company_id)
    if tx_type in ("in", "out"):
        q = q.filter_by(type=tx_type)
    if date_from:
        try:
            q = q.filter(CashTransaction.transaction_date >= date.fromisoformat(date_from))
        except ValueError:
            pass
    if date_to:
        try:
            q = q.filter(CashTransaction.transaction_date <= date.fromisoformat(date_to))
        except ValueError:
            pass

    transactions = q.order_by(CashTransaction.transaction_date.desc(), CashTransaction.id.desc()).all()

    # Companies for filter dropdown
    if current_user.has_role_at_least("manager"):
        companies = Company.query.filter_by(is_active=True).order_by(Company.company_name).all()
    else:
        companies = Company.query.filter_by(user_id=current_user.id, is_active=True).order_by(Company.company_name).all()

    return render_template("cash/transaction_list.html",
                           transactions=transactions, companies=companies,
                           selected_company_id=company_id, selected_type=tx_type,
                           date_from=date_from, date_to=date_to)


@cash_bp.route("/transactions/new", methods=["GET", "POST"])
@cash_access_required
def create_transaction():
    """Record a new cash transaction."""
    if request.method == "POST":
        company_id = request.form.get("company_id", type=int)
        tx_type = request.form.get("type", "in")
        amount = request.form.get("amount", type=float)
        currency = request.form.get("currency", "GBP").strip().upper()
        tx_date_str = request.form.get("transaction_date", "")
        description = request.form.get("description", "").strip()
        notes = request.form.get("notes", "").strip()
        method = request.form.get("method", "").strip() or None

        if not amount or amount <= 0 or tx_type not in ("in", "out"):
            flash("Please fill in all required fields correctly.", "danger")
            return redirect(url_for("cash.create_transaction"))

        if tx_type == "in" and not company_id:
            flash("Please select a company for cash in.", "danger")
            return redirect(url_for("cash.create_transaction"))

        if tx_type == "out" and method not in ("accounts", "bank"):
            flash("Please select a method for cash out.", "danger")
            return redirect(url_for("cash.create_transaction"))

        # Cash out has no company
        if tx_type == "out":
            company_id = None

        # Verify company ownership for non-managers (cash in only)
        if company_id and not current_user.has_role_at_least("manager"):
            company = db.session.get(Company, company_id)
            if not company or company.user_id != current_user.id:
                flash("Invalid company.", "danger")
                return redirect(url_for("cash.create_transaction"))

        try:
            tx_date = date.fromisoformat(tx_date_str) if tx_date_str else date.today()
        except ValueError:
            tx_date = date.today()

        tx = CashTransaction(
            company_id=company_id,
            user_id=current_user.id,
            type=tx_type,
            method=method if tx_type == "out" else None,
            amount=amount,
            currency=currency[:3],
            transaction_date=tx_date,
            description=description[:200],
            notes=notes,
        )
        db.session.add(tx)
        db.session.commit()

        flash(f"Cash {tx_type} of {currency} {amount:,.2f} recorded.", "success")
        return redirect(url_for("cash.dashboard"))

    # GET — show form
    prefill_company_id = request.args.get("company_id", type=int)
    if current_user.has_role_at_least("manager"):
        companies = Company.query.filter_by(is_active=True).order_by(Company.company_name).all()
    else:
        companies = Company.query.filter_by(user_id=current_user.id, is_active=True).order_by(Company.company_name).all()

    return render_template("cash/transaction_form.html",
                           companies=companies, transaction=None,
                           prefill_company_id=prefill_company_id,
                           today=date.today().isoformat())


@cash_bp.route("/transactions/<int:id>/edit", methods=["GET", "POST"])
@cash_access_required
def edit_transaction(id):
    """Edit an existing cash transaction."""
    tx = db.session.get(CashTransaction, id)
    if not tx:
        abort(404)

    # Users can only edit their own transactions
    if not current_user.has_role_at_least("manager") and tx.user_id != current_user.id:
        abort(403)

    if request.method == "POST":
        new_type = request.form.get("type", tx.type)
        new_amount = request.form.get("amount", type=float)
        new_company_id = request.form.get("company_id", type=int)
        new_method = request.form.get("method", "").strip() or None

        if new_type not in ("in", "out") or not new_amount or new_amount <= 0:
            flash("Invalid transaction data.", "danger")
            return redirect(url_for("cash.edit_transaction", id=id))

        if new_type == "in" and not new_company_id:
            flash("Please select a company for cash in.", "danger")
            return redirect(url_for("cash.edit_transaction", id=id))

        if new_type == "out" and new_method not in ("accounts", "bank"):
            flash("Please select a method for cash out.", "danger")
            return redirect(url_for("cash.edit_transaction", id=id))

        # Cash out has no company
        if new_type == "out":
            new_company_id = None

        # Verify company ownership for non-managers (cash in only)
        if new_company_id and not current_user.has_role_at_least("manager"):
            company = db.session.get(Company, new_company_id)
            if not company or company.user_id != current_user.id:
                flash("Invalid company.", "danger")
                return redirect(url_for("cash.edit_transaction", id=id))

        tx.company_id = new_company_id
        tx.type = new_type
        tx.method = new_method if new_type == "out" else None
        tx.amount = new_amount
        tx.currency = request.form.get("currency", tx.currency).strip().upper()[:3]
        tx_date_str = request.form.get("transaction_date", "")
        tx.description = request.form.get("description", "").strip()[:200]
        tx.notes = request.form.get("notes", "").strip()

        try:
            tx.transaction_date = date.fromisoformat(tx_date_str) if tx_date_str else tx.transaction_date
        except ValueError:
            pass

        db.session.commit()
        flash("Transaction updated.", "success")
        return redirect(url_for("cash.transaction_list"))

    if current_user.has_role_at_least("manager"):
        companies = Company.query.filter_by(is_active=True).order_by(Company.company_name).all()
    else:
        companies = Company.query.filter_by(user_id=current_user.id, is_active=True).order_by(Company.company_name).all()

    return render_template("cash/transaction_form.html",
                           companies=companies, transaction=tx,
                           prefill_company_id=tx.company_id,
                           today=date.today().isoformat())


@cash_bp.route("/transactions/<int:id>/delete", methods=["POST"])
@cash_access_required
def delete_transaction(id):
    """Delete a cash transaction."""
    tx = db.session.get(CashTransaction, id)
    if not tx:
        abort(404)

    if not current_user.has_role_at_least("manager") and tx.user_id != current_user.id:
        abort(403)

    db.session.delete(tx)
    db.session.commit()
    flash("Transaction deleted.", "success")
    return redirect(url_for("cash.transaction_list"))
