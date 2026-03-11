from flask import Blueprint

followups_bp = Blueprint("followups", __name__, template_folder="../../templates")

from blueprints.followups import routes  # noqa: E402, F401
