from flask import Blueprint, render_template, redirect, request, session, flash, url_for
import os

upload_data = Blueprint("upload_data", __name__)
upload_folder = "../upload"

@upload_data.route("/")
def upload_page():
    return render_template("load_batch.html")

@upload_data.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
    if not os.path.isdir(upload_folder):
        print("lol")
        os.mkdir(path=upload_folder)
    if request.method == 'POST':
        f = request.files['file']
        #Todo: use it
        f.save(os.path.join(upload_folder, f.filename))
        return render_template("load_batch.html", sucsess=True)