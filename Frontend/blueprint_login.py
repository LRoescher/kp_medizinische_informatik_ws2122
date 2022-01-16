from flask import Blueprint, render_template, redirect, request, session, flash, url_for
from Frontend.FlashMessageTypes import FlashMessageTypes
from Backend.interface import Interface
from Backend.backend_interface import BackendManager

access_control = Blueprint("access_control", __name__)
controller: Interface = BackendManager()


@access_control.before_app_request
def check_login():
    """
    before every page access check if the user is logged in
    """
    if request.endpoint is None:
        pass
    elif request.endpoint in ["access_control.login", "access_control.do_admin_login", "access_control.logout"]:
        return None
    elif request.endpoint.startswith("static"):
        # needed or the login form will get served without css :)
        return None

    elif request.endpoint == "favicon":
        # needed or the logo is missing in the login form
        return None

    if "logged_in" not in session or not session["logged_in"]:
        flash("Bitte loggen Sie sich zuerst ein.", FlashMessageTypes.FAILURE.value)
        return redirect(url_for("access_control.login"))
    else:
        session.modified = True


@access_control.route("/login")
def login():
    """
    render login template
    """
    return render_template("login.html", pagename="Login")


@access_control.route('/login', methods=['POST'])
def do_admin_login():
    """
    login the admin account
    """
    if request.form['password'] == 'password' and request.form['username'] == 'admin':
        session['logged_in'] = True
        session.permanent = True
        flash("Login erfolgreich!", FlashMessageTypes.SUCCESS.value)

        # ToDO: currently not working because is_db_empty also returns true when the db-connection fails
        # if not controller.is_db_empty():
        #     return redirect(url_for("results.get_analysis"))
        return redirect(url_for("main"))

    else:
        flash('Nutzername oder Passwort ist falsch!', FlashMessageTypes.FAILURE.value)
        return redirect(url_for("access_control.login"))


@access_control.route("/logout")
def logout():
    """
    logout the user
    """
    session['logged_in'] = False
    flash("Logout erfolgreich!")
    return redirect(url_for("access_control.login"))
