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
    return render_template("index.html")


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    # Data to send to Keycloak
    data = {
        "client_id": CLIENT_ID,
        "username": username,
        "password": password,
        "grant_type": "password",
    }
    try:
        response = requests.post(KEYCLOAK_URL, data=data, verify=False, timeout=1)
        logging.info("Keycloak response: %s", response.text)

        if response.status_code == 200:
            token_data = response.json()
            session["Authorization"] = token_data["access_token"]
            session["username"] = username
            session["role"] = "tbd"
            return jsonify({"success": True, "redirect": url_for("dashboard")})
        else:
            logging.error("Invalid credentials")
            return jsonify({"success": False, "message": "Invalid credentials"}), 401
    except requests.exceptions.RequestException:
        logging.error("Invalid credentials")
        return jsonify({"success": False, "message": "Invalid credentials"}), 401


@app.route("/dashboard", methods=["GET"])
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
    return jsonify({"success": True, "redirect": url_for("index")})
