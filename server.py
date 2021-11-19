from flask import Flask, render_template
import os

app = Flask(__name__, static_folder=os.path.abspath('templates/static'))


@app.route("/")
def home_page():
    return render_template("index.html")

@app.route("/login")
def login_page():
    return render_template("login.html")

@app.route("/register")
def register_page():
    return render_template("register.html")


@app.route("/password")
def forgot_password():
    return render_template("password.html")


@app.errorhandler(404)
def not_found_page(e):
    return render_template("404.html"),404


@app.errorhandler(401)
def unauth_page(e):
    return render_template("401.html"),401


@app.errorhandler(500)
def internal_error_page(e):
    return render_template("500.html"),500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)