from app import create_app
from flask import render_template, redirect, session, url_for
import logging

app = create_app()


@app.route("/")
def index():
    logging.info("Index page requested")
    return render_template("index.html")


@app.route("/teapot", methods=["POST"])
def dashboard():
    logging.info("Dashboard page requested")
    return "I'm a teapot from the POSD project app", 418


@app.route("/logout", methods=["POST"])
def logout():
    logging.info("Logout requested")
    session.pop("username", None)
    return redirect(url_for("index"))
