from datetime import datetime, date

from extensions import db

CONTACT_TYPES = ["phone", "email", "meeting"]

QUICK_FUNCTIONS = [
    {
        "id": "catalogue_sent",
        "label": "Latest catalogue sent",
        "icon": "bi-journal-richtext",
        "contact_type": "email",
        "notes": "Latest product catalogue sent",
        "outcome": "Catalogue delivered",
    },
    {
        "id": "price_list_sent",
        "label": "Price list sent",
        "icon": "bi-currency-pound",
        "contact_type": "email",
        "notes": "Current price list sent",
        "outcome": "Price list delivered",
    },
    {
        "id": "followup_call",
        "label": "Follow-up call made",
        "icon": "bi-telephone-outbound",
        "contact_type": "phone",
        "notes": "Routine follow-up call",
        "outcome": "Call completed",
    },
    {
        "id": "meeting_scheduled",
        "label": "Meeting scheduled",
        "icon": "bi-calendar-event",
        "contact_type": "meeting",
        "notes": "Meeting arranged",
        "outcome": "Meeting confirmed",
    },
    {
        "id": "quote_sent",
        "label": "Quote sent",
        "icon": "bi-receipt",
        "contact_type": "email",
        "notes": "Quotation sent",
        "outcome": "Quote delivered",
    },
]


class Contact(db.Model):
    __tablename__ = "contacts"

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(
        db.Integer, db.ForeignKey("clients.id"), nullable=False
    )
    date = db.Column(db.Date, nullable=False, default=date.today)
    time = db.Column(db.Time, nullable=True, default=None)
    contact_type = db.Column(db.String(20), nullable=False, default="phone")
    notes = db.Column(db.Text, default="")
    outcome = db.Column(db.String(200), default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Contact {self.contact_type} on {self.date}>"
