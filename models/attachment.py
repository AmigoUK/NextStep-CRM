from datetime import datetime

from extensions import db

# MIME type to Bootstrap icon mapping
_MIME_ICONS = {
    "image": "bi-file-image",
    "application/pdf": "bi-file-pdf",
    "application/vnd.ms-excel": "bi-file-earmark-spreadsheet",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "bi-file-earmark-spreadsheet",
    "application/msword": "bi-file-earmark-word",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "bi-file-earmark-word",
}


class Attachment(db.Model):
    __tablename__ = "attachments"

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(300), nullable=False)
    file_size = db.Column(db.Integer, default=0)
    mime_type = db.Column(db.String(100), default="")
    client_id = db.Column(
        db.Integer, db.ForeignKey("clients.id"), nullable=False
    )
    contact_id = db.Column(
        db.Integer, db.ForeignKey("contacts.id"), nullable=True
    )
    followup_id = db.Column(
        db.Integer, db.ForeignKey("followups.id"), nullable=True
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def file_size_display(self):
        if self.file_size < 1024:
            return f"{self.file_size} B"
        elif self.file_size < 1024 * 1024:
            return f"{self.file_size / 1024:.1f} KB"
        else:
            return f"{self.file_size / (1024 * 1024):.1f} MB"

    @property
    def icon(self):
        if self.mime_type:
            if self.mime_type in _MIME_ICONS:
                return _MIME_ICONS[self.mime_type]
            if self.mime_type.startswith("image"):
                return "bi-file-image"
        return "bi-file-earmark"

    def __repr__(self):
        return f"<Attachment {self.filename}>"
