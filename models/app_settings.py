from extensions import db


class AppSettings(db.Model):
    __tablename__ = "app_settings"

    id = db.Column(db.Integer, primary_key=True)
    theme = db.Column(db.String(20), nullable=False, default="light")

    @staticmethod
    def get():
        """Return the singleton settings row, auto-creating if missing."""
        settings = db.session.get(AppSettings, 1)
        if not settings:
            settings = AppSettings(id=1, theme="light")
            db.session.add(settings)
            db.session.commit()
        return settings

    def __repr__(self):
        return f"<AppSettings theme={self.theme}>"
