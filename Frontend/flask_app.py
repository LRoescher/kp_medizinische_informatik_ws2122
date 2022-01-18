from flask import Flask, render_template, send_from_directory, request, redirect, url_for
from datetime import timedelta
from Backend.interface import Interface, TranslationGerman, TranslationPercentagePims, TranslationPercentageKawasaki
from Backend.backend_interface import BackendManager
from Frontend.blueprint_person import person_data
from Frontend.blueprint_login import access_control
from Frontend.blueprint_results import results
from Frontend.blueprint_data_manager import data_manager
import os

analysis_color: dict = {
    "hue": 10,
    "saturation": 80,
    "lightness": 60
}
controller: Interface = BackendManager()

app = Flask(__name__, template_folder='./templates/')
app.jinja_options["lstrip_blocks"] = True
app.jinja_options["trim_blocks"] = True
app.permanent_session_lifetime = timedelta(minutes=5)   # 5 min auto logout

# blueprints
app.register_blueprint(access_control)
app.register_blueprint(person_data, url_prefix="/person_data")
app.register_blueprint(results, url_prefix="/results")
app.register_blueprint(data_manager)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


def translate(key: str) -> str:
    """
    translate Symptoms to German

    :param key: symptom
    :return: german identifier or input
    """
    return TranslationGerman[key] if key in TranslationGerman else key


@app.context_processor
def global_template_variables():
    """
    make this variables available in all templates
    """
    return {
        "db_empty": controller.is_db_empty(),
        "translate": translate,
        "analysis_color": analysis_color,
        "translation_kawasaki": TranslationPercentageKawasaki,
        "translation_pims": TranslationPercentagePims
    }


@app.route('/favicon.ico')
def favicon():
    """
    deliver page icon
    """
    return send_from_directory(os.path.join(app.root_path, 'static'), 'Icons/favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route("/")
def main():
    """
    render main page
    """
    return render_template("main.html", pagename="Startseite")


@app.route("/settings")
def settings():
    """
    render setting page
    """
    return render_template("settings.html", pagename="Einstellungen")


@app.route("/settings/color", methods=['POST'])
def set_color():
    """
    set the color for the analysis
    """
    analysis_color["hue"] = request.form['hue']
    analysis_color["saturation"] = request.form['saturation']
    analysis_color["lightness"] = request.form['lightness']

    return redirect(url_for("settings"))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
