from flask import Blueprint

cash_bp = Blueprint("cash", __name__, template_folder="../../templates")

from blueprints.cash import routes  # noqa: E402, F401
