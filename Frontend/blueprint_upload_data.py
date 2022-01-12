from flask import Blueprint, render_template, send_file, request, session, flash, url_for

from Backend.backend_interface import BackendManager
from Backend.interface import Interface
from config.definitions import ROOT_DIR
import os

upload_data = Blueprint("upload_data", __name__)
upload_folder = "../upload"
config_path = os.path.join(ROOT_DIR, "config", "config.yml")
controller: Interface = BackendManager()


@upload_data.route("/")
def upload_page():
    return render_template("load_batch.html")


@upload_data.route('/uploader', methods=['GET', 'POST'])
def upload_file():
    if not os.path.isdir(upload_folder):
        print("lol")
        os.mkdir(path=upload_folder)
    if request.method == 'POST':
        f = request.files['file']
        # Todo: use it

        if "config.yml" in f.filename:
            f.save(config_path)
            controller.reset_config()
        else:
            f.save(os.path.join(upload_folder, f.filename))
        return render_template("load_batch.html", sucsess=True)


@upload_data.route("/config")
def download_config():
    return send_file(config_path, as_attachment=True)
