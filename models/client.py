from extensions import db

CLIENT_STATUSES = ["lead", "prospect", "active", "inactive"]


class Client(db.Model):
    __tablename__ = "clients"

    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(200), nullable=False)
