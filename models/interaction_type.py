from datetime import datetime

from extensions import db

DEFAULT_INTERACTION_TYPES = [
    {"label": "phone", "icon": "bi-telephone", "colour": "#0d6efd"},
    {"label": "email", "icon": "bi-envelope", "colour": "#6f42c1"},
    {"label": "meeting", "icon": "bi-people", "colour": "#fd7e14"},
]


class InteractionType(db.Model):
    __tablename__ = "interaction_types"

    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(30), nullable=False, unique=True)
    icon = db.Column(db.String(50), nullable=False, default="bi-chat-dots")
    colour = db.Column(db.String(7), nullable=False, default="#0d6efd")
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {"label": self.label, "icon": self.icon, "colour": self.colour}

    def __repr__(self):
        return f"<InteractionType {self.label}>"
