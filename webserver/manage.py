from app import create_app
from flask import render_template, redirect, url_for, request, session, jsonify
import requests
import logging

app = create_app()
app.secret_key = "your_secret_key"
app.config["SESSION_TYPE"] = "filesystem"

# Keycloak configuration
KEYCLOAK_URL = app.config["KEYCLOAK_URL"]
CLIENT_ID = "Istio"


@app.route("/", methods=["GET"])
def index():
    if session.get("Authorization"):
        logging.info("User already logged in")
        return redirect(url_for("dashboard"))

    logging.info("User not logged in")
    return render_template("index.html", error=None)


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    data = {
        "client_id": CLIENT_ID,
        "username": username,
        "password": password,
        "grant_type": "password",
    }
    response = requests.post(KEYCLOAK_URL, data=data, verify=False)
    logging.info("Keycloak response: %s", response.text)

    if response.status_code == 200:
        token_data = response.json()
        session["Authorization"] = token_data["access_token"]
        session["username"] = username
        session["role"] = "tbd"
        return jsonify({"access_token": token_data["access_token"]})
    else:
        logging.error("Invalid credentials")
        return jsonify({"error": "Invalid credentials"}), 400


@app.route("/dashboard")
def dashboard():
    access_token = session.get("Authorization")
    if not access_token:
        logging.error("User not logged in")
        return redirect(url_for("index"))

    logging.info("User logged in")

    return render_template(
        "dashboard.html", username=session.get("username"), role=session.get("role")
    )


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    logging.info("User logged out")
    return redirect(url_for("index"))
