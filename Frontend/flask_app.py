from flask import Flask, flash, redirect, render_template, url_for, send_from_directory
from datetime import timedelta
from Backend.interface import Interface
from Frontend.FlashMessageTypes import FlashMessageTypes
from Frontend.blueprint_person import person_data
from Frontend.blueprint_login import access_control
from Frontend.blueprint_results import results
from Frontend.blueprint_upload_data import upload_data
import os

# ToDo: remove later
from Backend.example_interface import Example

controller: Interface = Example()

app = Flask(__name__, template_folder='./templates/')
app.jinja_options["lstrip_blocks"] = True
app.jinja_options["trim_blocks"] = True
app.permanent_session_lifetime = timedelta(minutes=5)   # 5 min auto logout

# blueprints
app.register_blueprint(access_control)
app.register_blueprint(person_data, url_prefix="/person_data")
app.register_blueprint(results, url_prefix="/results")
app.register_blueprint(upload_data, url_prefix="/upload_data")

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


@app.context_processor
def global_template_variables():
    return {
        "db_empty": controller.is_db_empty()
    }


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'Icons/favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route("/")
def main():
    return render_template("main.html", pagename="Startseite")


# @app.route("/<string:name>/")
# def pages(name):
#     # ToDo: remove
#     return render_template(name)


@app.route("/reset_db")
def reset_db():
    if controller.reset_db():
        flash("Database reset successful.", FlashMessageTypes.SUCCESS.value)
    else:
        flash("Database reset failed.", FlashMessageTypes.FAILURE.value)
    return redirect(url_for("main"))


if __name__ == "__main__":
    #ToDo: remove debug
    app.run(host='0.0.0.0', port=8080, debug=True)