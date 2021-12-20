from flask import Flask, flash, redirect, render_template, request, session, abort

app = Flask(__name__, template_folder='./templates/')
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.route("/")
def index():
    return render_template("login.html")

@app.route('/login', methods=['POST'])
def do_admin_login():
    if request.form['password'] == 'password' and request.form['username'] == 'admin':
        session['logged_in'] = True
        return pages("main.html")
    else:
        flash('wrong password!')
        return index()

@app.route("/logout")
def logout():
    session['logged_in'] = False
    return index()

@app.route("/<string:name>/")
def pages(name):
    if  session['logged_in']:
        return render_template(name)
    else:
        return index()



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)