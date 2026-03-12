from flask import Blueprint

attachments_bp = Blueprint("attachments", __name__)

from blueprints.attachments import routes  # noqa: E402, F401
