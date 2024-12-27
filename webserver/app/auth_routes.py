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
ADMIN_CLI_ID = "admin-cli"


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
            current_app.config["KEYCLOAK_REALM_ISTIO_OPENID_TOKEN_URL"],
            data=data,
            verify=False,
            timeout=1,
        )
        logging.info("Keycloak response: %s", response.text)

        if response.status_code == 200:
            token_data = response.json()
            session["Authorization"] = token_data["access_token"]
            session["refresh_token"] = token_data["refresh_token"]
            session["username"] = username
            admin_token = get_admin_token()
            user_id = get_user_id(admin_token, username)
            client_id = get_client_id(admin_token, CLIENT_ID)
            roles = get_user_roles(admin_token, user_id, client_id)
            session["role"] = roles[0]["name"]
            return jsonify({"success": True, "redirect": url_for("auth.dashboard")})
        else:
            logging.error("Invalid credentials")
            session.clear()
            return (
                jsonify({"success": False, "message": "Invalid credentials"}),
                401,
            )
    except requests.exceptions.RequestException:
        logging.error("Invalid credentials")
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
        "client_id": CLIENT_ID,
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


def get_admin_token():
    data = {
        "client_id": ADMIN_CLI_ID,
        "username": "admin",
        "password": "admin",
        "grant_type": "password",
    }
    try:
        response = requests.post(
            current_app.config["KEYCLOAK_REALM_MASTER_OPENID_TOKEN_URL"],
            data=data,
            verify=False,
            timeout=1,
        )
        logging.info("Keycloak response: %s", response.text)

        if response.status_code == 200:
            return response.json().get("access_token")
        else:
            logging.error("Invalid credentials")
            return None
    except requests.exceptions.RequestException:
        logging.error("Invalid credentials")
        return None


def get_user_id(admin_token, username):
    headers = {
        "Authorization": f"Bearer {admin_token}",
    }
    params = {"username": username}
    try:
        response = requests.get(
            current_app.config["KEYCLOAK_USERS_URL"],
            headers=headers,
            params=params,
            verify=False,
            timeout=1,
        )
        logging.info("Keycloak response: %s", response.text)

        if response.status_code == 200:
            return response.json()[0].get("id")
        else:
            logging.error("User not found")
            return None
    except requests.exceptions.RequestException:
        logging.error("User not found")
        return None


def get_client_id(admin_token, client_id):
    headers = {
        "Authorization": f"Bearer {admin_token}",
    }
    params = {"clientId": client_id}
    try:
        response = requests.get(
            current_app.config["KEYCLOAK_CLIENTS_URL"],
            headers=headers,
            params=params,
            verify=False,
            timeout=1,
        )
        logging.info("Keycloak response: %s", response.text)

        clients = response.json()
        for client in clients:
            if client.get("clientId") == client_id:
                return client.get("id")
    except requests.exceptions.RequestException:
        logging.error("Client not found")
        return None


def get_user_roles(admin_token, user_id, client_id):
    roles_url = f"{current_app.config['KEYCLOAK_USERS_URL']}/{user_id}/role-mappings/clients/{client_id}"
    headers = {
        "Authorization": f"Bearer {admin_token}",
    }
    try:
        response = requests.get(
            roles_url,
            headers=headers,
            verify=False,
            timeout=1,
        )
        logging.info("Keycloak response: %s", response.text)

        return response.json()
    except requests.exceptions.RequestException:
        logging.error("Roles not found")
        return None
