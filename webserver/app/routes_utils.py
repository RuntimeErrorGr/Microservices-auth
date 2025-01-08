import logging
import requests
from flask import session, current_app, redirect, url_for


class NoPermissionError(Exception):
    """Raised when the user does not have permission to access the requested resource."""


class User:
    def __init__(self, username, role, id):
        self.username = username
        self.role = role
        self.id = id

    def __repr__(self):
        return f"User(username={self.username}, role={self.role}, id={self.id})"

    def to_dict(self):
        return {
            "username": self.username,
            "role": self.role,
            "id": self.id,
        }


ISTIO_CLIENT_ID = "Istio"
ADMIN_CLIENT_CLI_ID = "admin-cli"


def make_authenticated_get_request(url):
    with current_app.app_context():
        access_token = session.get("Authorization")
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    try:
        response = requests.get(url, timeout=5, headers=headers)
        if response.status_code in [401, 403]:
            logging.error(
                f"Failed FETCH request: {response.status_code} {response.text}"
            )
            raise NoPermissionError

        if not response.headers.get("Content-Type") == "application/json":
            return response.text
        logging.info(f"Response: {response.json()}")
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error connecting to books service: {e}")
        return None


def make_authenticated_post_request(url, data):
    with current_app.app_context():
        access_token = session.get("Authorization")
    header = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(url, headers=header, json=data)
        if response.status_code in [401, 403]:
            logging.error(f"Failed POST data: {response.status_code} {response.text}")
            raise NoPermissionError

        if not response.headers.get("Content-Type") == "application/json":
            return response.text
        logging.info(f"Response: {response.json()}")
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error connecting to books service: {e}")
        return None


def make_authenticated_delete_request(url):
    with current_app.app_context():
        access_token = session.get("Authorization")
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    try:
        response = requests.delete(url, timeout=5, headers=headers)
        if response.status_code in [401, 403]:
            logging.error(
                f"Failed DELETE request: {response.status_code} {response.text}"
            )
            raise NoPermissionError

        if not response.headers.get("Content-Type") == "application/json":
            return response.text
        logging.info(f"Response: {response.json()}")
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error connecting to books service: {e}")
        return None


def make_authenticated_put_request(url, data):
    with current_app.app_context():
        access_token = session.get("Authorization")
    header = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    try:
        response = requests.put(url, headers=header, json=data)
        if response.status_code in [401, 403]:
            logging.error(f"Failed PUT request: {response.status_code} {response.text}")
            raise NoPermissionError

        if not response.headers.get("Content-Type") == "application/json":
            return response.text
        logging.info(f"Response: {response.json()}")
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error connecting to books service: {e}")
        return None


def get_admin_token():
    data = {
        "client_id": ADMIN_CLIENT_CLI_ID,
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


def get_client_id(admin_token):
    headers = {
        "Authorization": f"Bearer {admin_token}",
    }
    params = {"clientId": ISTIO_CLIENT_ID}
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
            if client.get("clientId") == ISTIO_CLIENT_ID:
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
        return [role.get("name") for role in response.json()]
    except requests.exceptions.RequestException:
        logging.error("Roles not found")
        return None


def get_users(admin_token, client_id):
    users_url = current_app.config['KEYCLOAK_USERS_URL']
    headers = {
        "Authorization": f"Bearer {admin_token}",
    }
    try:
        response = requests.get(
            users_url,
            headers=headers,
            verify=False,
            timeout=1,
        )
        logging.info("Keycloak response: %s", response.text)
        raw_users = response.json()

        users = []
        for user_data in raw_users:
            username = user_data.get("username")
            user_id = user_data.get("id")
            roles = get_user_roles(admin_token, user_id, client_id)
            if roles:
                role = roles[0]
            else:
                role = None
            users.append(User(username=username, role=role, id=user_id))
        return users

    except requests.exceptions.RequestException:
        logging.error("Users not found")
        return None


def get_roles(admin_token, client_id):
    roles_url = f"{current_app.config['KEYCLOAK_CLIENTS_URL']}/{client_id}/roles"
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
        raw_roles = response.json()
        roles = []
        for role_data in raw_roles:
            name = role_data.get("name")
            roles.append(name)
        logging.info("Roles: %s", roles)
        return roles

    except requests.exceptions.RequestException:
        logging.error("Users not found")
        return None


def change_role(username, role_name):
    delete_role(username)  # first delete the role, because it will otherwise just add one after the other
    admin_token = get_admin_token()
    client_id = get_client_id(admin_token)
    headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }
    get_role_id_by_role_name_url = f"{current_app.config['KEYCLOAK_CLIENTS_URL']}/{client_id}/roles/{role_name}"
    response = requests.get(
        get_role_id_by_role_name_url,
        headers=headers,
        verify=False,
        timeout=1
    )
    logging.info("Keycloak response: %s", response.text)
    raw_role = response.json()

    role_id = raw_role.get("id")

    users = session.get('users')
    user_id = 0
    for user in users:
        if user.get("username") == username:
            user_id = user.get("id")
    logging.info(
        f"Change role of user with username {username} and user_id {user_id} to role_name {role_name} and role_id {role_id}")
    change_role_url = f"{current_app.config['KEYCLOAK_USERS_URL']}/{user_id}/role-mappings/clients/{client_id}"
    role_payload = [
        {"id": role_id,
         "name": role_name}
    ]
    try:
        response = requests.post(
            change_role_url,
            json=role_payload,
            headers=headers,
            verify=False,
            timeout=1
        )
        logging.info("Keycloak response: %s", response.text)
        if response.status_code == 204:
            logging.info("Role assigned successfully.")
            return True
        else:
            logging.error("Failed to assign role. Status code: %d", response.status_code)
            logging.error("Response: %s", response.text)
            return False

    except requests.exceptions.RequestException as e:
        logging.error(f"An error occurred while changing the role: {e}")
        return False


def delete_role(username):
    users = session.get('users')
    user_id = 0
    for user in users:
        if user.get("username") == username:
            user_id = user.get("id")
    admin_token = get_admin_token()
    client_id = get_client_id(admin_token)
    logging.info(f"Delete role of user with {username} and {user_id}")
    delete_role_url = f"{current_app.config['KEYCLOAK_USERS_URL']}/{user_id}/role-mappings/clients/{client_id}"
    headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.delete(
            delete_role_url,
            headers=headers,
            verify=False,
            timeout=1
        )
        logging.info("Keycloak response: %s", response.text)
        if response.status_code == 204:
            logging.info("Role deleted successfully.")
            return True
        else:
            logging.error("Failed to delete role. Status code: %d", response.status_code)
            logging.error("Response: %s", response.text)
            return False

    except requests.exceptions.RequestException as e:
        logging.error(f"An error occurred while changing the role: {e}")
        return False


def update_role():
    with current_app.app_context():
        try:
            if session.get("Authorization"):
                admin_token = get_admin_token()
                user_id = session.get("keycloak_user_id")
                client_id = get_client_id(admin_token)

                updated_roles = get_user_roles(admin_token, user_id, client_id)
                new_role = "-".join(updated_roles)
                logging.info("Roles: %s -> %s", session.get("role"), new_role)
                if new_role != session.get("role"):
                    refresh_token = session.get("refresh_token")
                    if refresh_token:
                        data = {
                            "client_id": ISTIO_CLIENT_ID,
                            "grant_type": "refresh_token",
                            "refresh_token": refresh_token,
                        }
                        response = requests.post(
                            current_app.config["KEYCLOAK_REALM_ISTIO_OPENID_TOKEN_URL"],
                            data=data,
                            verify=False,
                            timeout=1,
                        )
                        if response.status_code == 200:
                            token_data = response.json()
                            session["Authorization"] = token_data["access_token"]
                            session["refresh_token"] = token_data["refresh_token"]
                            session["role"] = new_role
                            logging.info("Access token refreshed, and role updated.")
                        else:
                            logging.error("Failed to refresh access token.")
                            session.clear()
                            return redirect(url_for("auth.login"))
                    else:
                        logging.warning("Refresh token is missing. Clearing session.")
                        session.clear()
                        return redirect(url_for("auth.login"))
        except requests.exceptions.RequestException as e:
            logging.error("Error during role update or token refresh: %s", str(e))
            session.clear()
            return redirect(url_for("auth.login"))
