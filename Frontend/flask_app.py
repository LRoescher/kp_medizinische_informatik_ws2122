from flask import Flask, flash, redirect, render_template, url_for, send_from_directory
from datetime import timedelta
from Backend.interface import Interface, TranslationGerman
from Backend.backend_interface import BackendManager
from Frontend.FlashMessageTypes import FlashMessageTypes
from Frontend.blueprint_person import person_data
from Frontend.blueprint_login import access_control
from Frontend.blueprint_results import results
from Frontend.blueprint_data_manager import data_manager
from Backend.example_interface import Example
import os


controller: Interface = Example()

app = Flask(__name__, template_folder='./templates/')
app.jinja_options["lstrip_blocks"] = True
app.jinja_options["trim_blocks"] = True
#ToDo: change
app.permanent_session_lifetime = timedelta(minutes=5)   # 5 min auto logout

# blueprints
app.register_blueprint(access_control)
app.register_blueprint(person_data, url_prefix="/person_data")
app.register_blueprint(results, url_prefix="/results")
app.register_blueprint(data_manager)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


def translate(key: str) -> str:
    '''
    translate Symptoms to German

    :param key: symptom
    :return: german identifier or input
    '''
    return TranslationGerman[key] if key in TranslationGerman else key


@app.context_processor
def global_template_variables():
    return {
        "db_empty": controller.is_db_empty(),
        "translate": translate
    }


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'Icons/favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route("/")
def main():
    return render_template("main.html", pagename="Startseite")


@app.route("/settings")
def settings():
    return render_template("settings.html", pagename="Einstellungen")


if __name__ == "__main__":
    #ToDo: remove debug
    app.run(host='0.0.0.0', port=8080, debug=True)