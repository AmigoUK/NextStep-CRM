from flask import Blueprint

contacts_bp = Blueprint("contacts", __name__, template_folder="../../templates")

from blueprints.contacts import routes  # noqa: E402, F401
