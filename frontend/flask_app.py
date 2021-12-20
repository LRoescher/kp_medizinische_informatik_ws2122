from flask import Flask, flash, redirect, render_template, request, session, abort
import os
app = Flask(__name__, template_folder='./templates/')

@app.route("/")
def index():
    return render_template("main.html")

@app.route("/<string:name>/")
def hello(name):
    return render_template(name)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)