from flask import Flask, flash, redirect, render_template, request, session, url_for, g
from Backend.interface import PatientId, Interface
from typing import Callable

# ToDo: remove later
from Backend.example_interface import Example

controller: Interface = Example()

app = Flask(__name__, template_folder='./templates/')
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


@app.before_request
def check_login():
    if request.endpoint in ["login", "do_admin_login", "logout"]:
        return None

    if "logged_in" not in session or not session["logged_in"]:
        return redirect("login")


@app.route("/")
def main():
    return redirect(url_for("pages", name="main.html"))


@app.route("/login")
def login():
    return render_template("login.html")


@app.route('/login', methods=['POST'])
def do_admin_login():
    if request.form['password'] == 'password' and request.form['username'] == 'admin':
        session['logged_in'] = True
        return redirect(url_for("pages", name="main.html"))
    else:
        flash('wrong password!')
        return login()


@app.route("/logout")
def logout():
    session['logged_in'] = False
    return redirect("login")


@app.route("/<string:name>/")
def pages(name):
    return render_template(name)


@app.route("/analysis")
def get_analysis():
    # ToDo: login
    return render_template("analysis.html", analysis_data=controller.analysis_data)


@app.route("/person_data")
def get_empty_person_data():
    #ToDo: implement
    pass


@app.route("/person_data/<int:patient_id>")
def get_person_data(patient_id: PatientId):
    #ToDo: implement
    pass


@app.route("/person_data/save")
def add_person_date():
    #ToDo: implement
    pass


@app.route("/person_data/<int:patient_id>/save")
def update_person(patient_id: PatientId):
    #ToDo: implement
    pass


@app.route("/result/<int:patient_id>/pims")
def result_pims(patient_id: PatientId):
    #ToDo: implement
    pass


@app.route("/result/<int:patient_id>/kawasaki")
def result_kawasaki(patient_id: int):
    #ToDo: implement
    pass


if __name__ == "__main__":
    #ToDo: remove debug
    app.run(host='0.0.0.0', port=8080, debug=True)