from extensions import db

PRIORITIES = ["high", "medium", "low"]


class FollowUp(db.Model):
    __tablename__ = "followups"

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False)
