from flask import render_template

from blueprints.clients import clients_bp


@clients_bp.route("/")
def list_clients():
    return render_template("clients/list.html")
