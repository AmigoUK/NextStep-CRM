from flask import Blueprint

orders_bp = Blueprint("accounts", __name__, template_folder="../../templates")

from blueprints.orders import routes  # noqa: E402, F401
