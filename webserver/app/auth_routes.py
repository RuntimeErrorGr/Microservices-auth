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
from . import routes_utils as utils

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/", methods=["GET"])
def index():
    if session.get("Authorization"):
        logging.info("User already logged in")
        return redirect(url_for("auth.dashboard"))
    logging.info("User not logged in")
    return render_template("index.html")


@auth_bp.route("/teapot", methods=["GET"])
def teapot():
    return "I'm a teapot from the POSD project app", 418


@auth_bp.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    
    logging.info("Login attempt for user: %s", username)

    data = f"client_id=Istio&username={username}&password={password}&grant_type=password"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': '*/*',
    }

    try:
        response = requests.post(
            current_app.config["KEYCLOAK_REALM_ISTIO_OPENID_TOKEN_URL"],
            data=data,
            headers=headers,
            verify=False,
            timeout=5
        )
        
        logging.info("Keycloak response code: %d", response.status_code)

        if response.status_code == 200:
            token_data = response.json()
            session["Authorization"] = token_data["access_token"]
            session["refresh_token"] = token_data["refresh_token"]
            session["username"] = username
            admin_token = utils.get_admin_token()
            user_id = utils.get_user_id(admin_token, username)
            session["keycloak_user_id"] = user_id
            client_id = utils.get_client_id(admin_token)
            roles = utils.get_user_roles(admin_token, user_id, client_id)
            
            # Special handling for admin
            if username == 'admin':
                roles = ['admin']
                
            session["role"] = "-".join(roles)
            session["user_roles"] = roles  # Add this line
            
            logging.info("Role: %s, User roles: %s", session["role"], session.get("user_roles", []))
            return jsonify({"success": True, "redirect": url_for("auth.dashboard")})
        else:
            logging.error("Login failed with status %s: %s", response.status_code, response.text)
            session.clear()
            return (
                jsonify({"success": False, "message": "Invalid credentials"}),
                401,
            )
    except requests.exceptions.RequestException as e:
        logging.error("Request exception during login: %s", str(e))
        session.clear()
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
        "client_id": utils.ISTIO_CLIENT_ID,
        "refresh_token": session.get("refresh_token"),
    }
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    try:
        response = requests.post(
            current_app.config["KEYCLOAK_REALM_ISTIO_OPENID_LOGOUT_URL"],
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
