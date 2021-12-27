from flask import Blueprint, render_template, redirect, request, session, flash, url_for
from Frontend.FlashMessageTypes import FlashMessageTypes

access_control = Blueprint("access_control", __name__)


@access_control.before_app_request
def check_login():
    if request.endpoint in ["access_control.login", "access_control.do_admin_login", "access_control.logout"]:
        return None
    elif request.endpoint.startswith("static"):
        # needed or the login form will get served without css :)
        return None

    if "logged_in" not in session or not session["logged_in"]:
        return redirect(url_for("access_control.login"))
    else:
        session.modified = True


@access_control.route("/login")
def login():
    return render_template("login.html")


@access_control.route('/login', methods=['POST'])
def do_admin_login():
    if request.form['password'] == 'password' and request.form['username'] == 'admin':
        session['logged_in'] = True
        session.permanent = True
        flash("Login success", FlashMessageTypes.SUCCESS.value)
        return redirect(url_for("main"))
    else:
        flash('wrong password!', FlashMessageTypes.FAILURE.value)
        return redirect(url_for("access_control.login"))


@access_control.route("/logout")
def logout():
    session['logged_in'] = False
    return redirect(url_for("access_control.login"))
