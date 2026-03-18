"""CSV import/export for invoices."""

import csv
import io
from datetime import datetime

from sqlalchemy import func

from extensions import db
from models.company import Company
from models.invoice import INVOICE_STATUSES, Invoice


INVOICE_COLUMNS = [
    "invoice_number", "internal_company_id", "amount", "currency",
    "issue_date", "due_date", "paid_date", "paid_amount", "status", "notes",
]


def _read_csv(file_stream):
    raw = file_stream.read()
    if isinstance(raw, bytes):
        text = raw.decode("utf-8-sig")
    else:
        text = raw.lstrip("\ufeff")

    sample = text[:4096]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
    except csv.Error:
        dialect = csv.excel

    reader = csv.DictReader(io.StringIO(text), dialect=dialect)
    headers = reader.fieldnames or []
    rows = list(reader)
    return headers, rows


def _parse_date(value, field_name="date"):
    if not value or not str(value).strip():
        return None, None
    try:
        return datetime.strptime(value.strip(), "%Y-%m-%d").date(), None
    except ValueError:
        return None, f"Invalid {field_name} format (expected YYYY-MM-DD): '{value}'"


def _parse_float(value, field_name="amount"):
    if not value or not str(value).strip():
        return None, None
    try:
        return float(value.strip()), None
    except ValueError:
        return None, f"Invalid {field_name} (expected number): '{value}'"


def generate_export_csv():
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=INVOICE_COLUMNS)
    writer.writeheader()

    invoices = (
        db.session.query(Invoice, Company.internal_id)
        .join(Company, Invoice.company_id == Company.id)
        .order_by(Invoice.issue_date.desc())
        .all()
    )

    for inv, internal_id in invoices:
        writer.writerow({
            "invoice_number": inv.invoice_number,
            "internal_company_id": internal_id or "",
            "amount": inv.amount,
            "currency": inv.currency,
            "issue_date": inv.issue_date.isoformat() if inv.issue_date else "",
            "due_date": inv.due_date.isoformat() if inv.due_date else "",
            "paid_date": inv.paid_date.isoformat() if inv.paid_date else "",
            "paid_amount": inv.paid_amount if inv.paid_amount else "",
            "status": inv.status,
            "notes": inv.notes or "",
        })

    output.seek(0)
    return output


def generate_template_csv():
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=INVOICE_COLUMNS)
    writer.writeheader()
    writer.writerow({
        "invoice_number": "INV-001",
        "internal_company_id": "ACME-001",
        "amount": "1500.00",
        "currency": "GBP",
        "issue_date": "2026-01-15",
        "due_date": "2026-02-15",
        "paid_date": "",
        "paid_amount": "",
        "status": "unpaid",
        "notes": "January services",
    })
    writer.writerow({
        "invoice_number": "INV-002",
        "internal_company_id": "ACME-001",
        "amount": "2000.00",
        "currency": "GBP",
        "issue_date": "2025-12-01",
        "due_date": "2026-01-01",
        "paid_date": "2025-12-28",
        "paid_amount": "2000.00",
        "status": "paid",
        "notes": "December services",
    })
    output.seek(0)
    return output


def validate_and_import(file_stream, upsert=False):
    """Parse, validate, and import invoice CSV data.

    Returns dict with keys: imported, updated, skipped, errors, warnings.
    """
    headers, rows = _read_csv(file_stream)

    if not rows:
        return {"imported": 0, "updated": 0, "skipped": 0, "errors": [], "warnings": ["File is empty or contains only headers."]}

    errors = []
    warnings = []
    valid_records = []

    for i, row in enumerate(rows, start=2):
        row_errors = []

        invoice_number = row.get("invoice_number", "").strip()
        if not invoice_number:
            row_errors.append("invoice_number is required")

        internal_id = row.get("internal_company_id", "").strip()
        if not internal_id:
            row_errors.append("internal_company_id is required")
        else:
            company = Company.query.filter(
                func.lower(Company.internal_id) == internal_id.lower()
            ).first()
            if not company:
                row_errors.append(f"No company found with internal_id: '{internal_id}'")

        amount, amount_err = _parse_float(row.get("amount", ""), "amount")
        if amount_err:
            row_errors.append(amount_err)
        elif amount is None:
            row_errors.append("amount is required")

        currency = row.get("currency", "").strip().upper() or "GBP"
        if len(currency) != 3:
            row_errors.append(f"Invalid currency code: '{currency}'")

        issue_date, issue_err = _parse_date(row.get("issue_date", ""), "issue_date")
        if issue_err:
            row_errors.append(issue_err)
        elif issue_date is None:
            row_errors.append("issue_date is required")

        due_date, due_err = _parse_date(row.get("due_date", ""), "due_date")
        if due_err:
            row_errors.append(due_err)
        elif due_date is None:
            row_errors.append("due_date is required")

        paid_date, paid_err = _parse_date(row.get("paid_date", ""), "paid_date")
        if paid_err:
            row_errors.append(paid_err)

        paid_amount, pa_err = _parse_float(row.get("paid_amount", ""), "paid_amount")
        if pa_err:
            row_errors.append(pa_err)

        status = row.get("status", "").strip().lower() or "unpaid"
        if status not in INVOICE_STATUSES:
            row_errors.append(f"Invalid status: '{status}' (valid: {', '.join(INVOICE_STATUSES)})")

        if row_errors:
            errors.append({
                "row": i,
                "data": dict(row),
                "error": "; ".join(row_errors),
            })
            continue

        valid_records.append({
            "invoice_number": invoice_number,
            "company_id": company.id,
            "amount": amount,
            "currency": currency,
            "issue_date": issue_date,
            "due_date": due_date,
            "paid_date": paid_date,
            "paid_amount": paid_amount,
            "status": status,
            "notes": row.get("notes", "").strip(),
        })

    imported = 0
    updated = 0
    try:
        for rec in valid_records:
            existing = Invoice.query.filter_by(invoice_number=rec["invoice_number"]).first()
            if existing and upsert:
                existing.paid_date = rec["paid_date"]
                existing.paid_amount = rec["paid_amount"]
                existing.status = rec["status"]
                existing.notes = rec["notes"]
                updated += 1
            elif existing:
                warnings.append(f"Row with invoice_number '{rec['invoice_number']}' already exists (skipped). Enable upsert to update.")
            else:
                db.session.add(Invoice(**rec))
                imported += 1
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        warnings.append(f"Database error: {e}")
        imported = 0
        updated = 0

    return {
        "imported": imported,
        "updated": updated,
        "skipped": len(errors),
        "errors": errors,
        "warnings": warnings,
    }
