from datetime import date, datetime

from extensions import db


class CashTransaction(db.Model):
    __tablename__ = "cash_transactions"

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    type = db.Column(db.String(3), nullable=False)  # "in" or "out"
    method = db.Column(db.String(20))  # "accounts" or "bank" (cash out only)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), nullable=False, default="GBP")
    transaction_date = db.Column(db.Date, nullable=False, default=date.today)
    description = db.Column(db.String(200))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    company = db.relationship("Company", backref=db.backref("cash_transactions", lazy="dynamic"))
    user = db.relationship("User", backref=db.backref("cash_transactions", lazy="dynamic"))

    def __repr__(self):
        return f"<CashTransaction {self.type} {self.amount} {self.currency}>"
