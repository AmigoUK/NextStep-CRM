from flask import render_template

from blueprints.contacts import contacts_bp


@contacts_bp.route("/")
def list_contacts():
    return render_template("contacts/list.html")
