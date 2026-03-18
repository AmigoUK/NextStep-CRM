import json

from extensions import db

DEFAULT_COMPANY_COLUMNS = {
    "columns": {
        "internal_id":      {"label": "ID",              "desktop": True,  "tablet": False, "mobile": False},
        "company_name":     {"label": "Company",         "desktop": True,  "tablet": True,  "mobile": True,  "locked": True},
        "contact_person":   {"label": "Contact Person",  "desktop": True,  "tablet": True,  "mobile": False},
        "industry":         {"label": "Industry",        "desktop": True,  "tablet": False, "mobile": False},
        "status":           {"label": "Status",          "desktop": True,  "tablet": True,  "mobile": True},
        "last_interaction": {"label": "Last Interaction", "desktop": True,  "tablet": True,  "mobile": False},
        "next_followup":    {"label": "Next Follow-up",  "desktop": True,  "tablet": False, "mobile": False},
        "owner":            {"label": "Owner",           "desktop": True,  "tablet": False, "mobile": False},
        "actions":          {"label": "Actions",         "desktop": True,  "tablet": True,  "mobile": True,  "locked": True},
    }
}


class AppSettings(db.Model):
    __tablename__ = "app_settings"

    id = db.Column(db.Integer, primary_key=True)
    theme = db.Column(db.String(20), nullable=False, default="light")
    sticky_navbar = db.Column(db.Boolean, nullable=False, default=True)
    pagination_enabled = db.Column(db.Boolean, nullable=False, default=True)
    pagination_size = db.Column(db.Integer, nullable=False, default=25)
    back_to_top = db.Column(db.Boolean, nullable=False, default=True)
    risk_assessment_mode = db.Column(db.String(10), nullable=False, default="full")
    company_list_columns = db.Column(db.Text, default="{}")
    show_deactivated_to_managers = db.Column(db.Boolean, default=True)
    show_deactivated_to_users = db.Column(db.Boolean, default=False)

    @property
    def company_columns_config(self):
        raw = json.loads(self.company_list_columns or "{}")
        if not raw or "columns" not in raw:
            return DEFAULT_COMPANY_COLUMNS
        return raw

    @company_columns_config.setter
    def company_columns_config(self, value):
        self.company_list_columns = json.dumps(value)

    @staticmethod
    def get():
        """Return the singleton settings row, auto-creating if missing."""
        settings = db.session.get(AppSettings, 1)
        if not settings:
            settings = AppSettings(
                id=1,
                theme="light",
                sticky_navbar=True,
                pagination_enabled=True,
                pagination_size=25,
                back_to_top=True,
                risk_assessment_mode="full",
            )
            db.session.add(settings)
            db.session.commit()
        return settings

    def __repr__(self):
        return f"<AppSettings theme={self.theme}>"
