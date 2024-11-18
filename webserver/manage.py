from app import create_app
from flask import render_template, redirect, request, session, url_for
import logging

app = create_app()


@app.route("/")
def index():
    logging.info("Index page requested")
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    logging.info("Dashboard page requested")
    if "access_token" in session:
        return render_template("dashboard.html")
    else:
        return redirect(url_for("index"))


@app.route("/logout", methods=["POST"])
def logout():
    logging.info("Logout requested")
    session.pop("username", None)
    return redirect(url_for("index"))
