# app.py
from flask import Flask, render_template, redirect, request, session, url_for
from flask_cors import CORS
from server import server_bp, licenses
import os

app = Flask(__name__)
app.secret_key = "supersecret"  # Replace in prod
CORS(app)

app.register_blueprint(server_bp)

USERNAME = "admin"
PASSWORD = "password"

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == USERNAME and request.form["password"] == PASSWORD:
            session["logged_in"] = True
            return redirect("/dashboard")
        return "Invalid credentials", 403
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if not session.get("logged_in"):
        return redirect("/")
    return render_template("dashboard.html", licenses=licenses)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(port=5000, debug=True)
