from datetime import date, datetime

from extensions import db

INVOICE_STATUSES = ["unpaid", "paid", "partially_paid", "cancelled", "credited"]


class Invoice(db.Model):
    __tablename__ = "invoices"

    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(100), unique=True, nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), nullable=False, default="GBP")
    issue_date = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    paid_date = db.Column(db.Date, nullable=True)
    paid_amount = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(20), nullable=False, default="unpaid")
    notes = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    @property
    def is_overdue(self):
        return (
            self.status in ("unpaid", "partially_paid")
            and self.due_date is not None
            and self.due_date < date.today()
        )

    @property
    def payment_days(self):
        """Days between due_date and paid_date (or today if unpaid)."""
        if not self.due_date:
            return 0
        end = self.paid_date if self.paid_date else date.today()
        return (end - self.due_date).days

    def __repr__(self):
        return f"<Invoice {self.invoice_number}>"
