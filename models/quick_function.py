from datetime import datetime

from extensions import db

DEFAULT_QUICK_FUNCTIONS = [
    {
        "label": "Latest catalogue sent",
        "icon": "bi-journal-richtext",
        "contact_type": "email",
        "notes": "Latest product catalogue sent",
        "outcome": "Catalogue delivered",
    },
    {
        "label": "Price list sent",
        "icon": "bi-currency-pound",
        "contact_type": "email",
        "notes": "Current price list sent",
        "outcome": "Price list delivered",
    },
    {
        "label": "Follow-up call made",
        "icon": "bi-telephone-outbound",
        "contact_type": "phone",
        "notes": "Routine follow-up call",
        "outcome": "Call completed",
    },
    {
        "label": "Meeting scheduled",
        "icon": "bi-calendar-event",
        "contact_type": "meeting",
        "notes": "Meeting arranged",
        "outcome": "Meeting confirmed",
    },
    {
        "label": "Quote sent",
        "icon": "bi-receipt",
        "contact_type": "email",
        "notes": "Quotation sent",
        "outcome": "Quote delivered",
    },
]


class QuickFunction(db.Model):
    __tablename__ = "quick_functions"

    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(100), nullable=False)
    icon = db.Column(db.String(50), nullable=False, default="bi-lightning-charge")
    contact_type = db.Column(db.String(20), nullable=False, default="phone")
    notes = db.Column(db.String(200), default="")
    outcome = db.Column(db.String(200), default="")
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "label": self.label,
            "icon": self.icon,
            "contact_type": self.contact_type,
            "notes": self.notes,
            "outcome": self.outcome,
        }

    def __repr__(self):
        return f"<QuickFunction {self.label}>"
