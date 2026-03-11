from flask import render_template

from blueprints.followups import followups_bp


@followups_bp.route("/")
def list_followups():
    return render_template("followups/list.html")
