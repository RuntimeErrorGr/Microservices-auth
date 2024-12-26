from flask import (
    Blueprint,
    request,
    session,
    current_app,
    jsonify,
    redirect,
    url_for,
    render_template,
)
import requests
import logging

auth_bp = Blueprint("auth", __name__)

CLIENT_ID = "Istio"


@auth_bp.route("/", methods=["GET"])
def index():
    if session.get("Authorization"):
        logging.info("User already logged in")
        return redirect(url_for("auth.dashboard"))
    logging.info("User not logged in")
    return render_template("index.html")


@auth_bp.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    data = {
        "client_id": CLIENT_ID,
        "username": username,
        "password": password,
        "grant_type": "password",
    }
    try:
        response = requests.post(
            current_app.config["KEYCLOAK_URL"], data=data, verify=False, timeout=1
        )
        logging.info("Keycloak response: %s", response.text)

        if response.status_code == 200:
            token_data = response.json()
            session["Authorization"] = token_data["access_token"]
            session["refresh_token"] = token_data["refresh_token"]
            session["username"] = username
            session["role"] = "tbd"
            return jsonify({"success": True, "redirect": url_for("auth.dashboard")})
        else:
            logging.error("Invalid credentials")
            return jsonify({"success": False, "message": "Invalid credentials"}), 401
    except requests.exceptions.RequestException:
        logging.error("Invalid credentials")
        return jsonify({"success": False, "message": "Invalid credentials"}), 401


@auth_bp.route("/dashboard", methods=["GET"])
def dashboard():
    access_token = session.get("Authorization")
    if not access_token:
        logging.error("User not logged in")
        return redirect(url_for("auth.index"))

    logging.info("User logged in")
    return render_template(
        "dashboard.html", username=session.get("username"), role=session.get("role")
    )


@auth_bp.route("/logout", methods=["POST"])
def logout():
    access_token = session.get("Authorization")
    if not access_token:
        return jsonify({"success": False, "message": "No active session"}), 400

    data = {
        "client_id": CLIENT_ID,
        "refresh_token": session.get("refresh_token"),
    }
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    try:
        response = requests.post(
            current_app.config["KEYCLOAK_LOGOUT_URL"],
            data=data,
            headers=headers,
            verify=False,
        )
        if response.status_code in [200, 201, 202, 203, 204]:
            session.clear()
            return jsonify({"success": True, "redirect": url_for("auth.index")})
        else:
            logging.error(f"Logout failed: {response.text}")
            return (
                jsonify({"success": False, "message": "Logout failed"}),
                response.status_code,
            )
    except requests.exceptions.RequestException as e:
        logging.error(f"Error during logout: {e}")
        return jsonify({"success": False, "message": "Error during logout"}), 500
