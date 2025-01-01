import logging
import requests
from flask import session, current_app


class NoPermissionError(Exception):
    """Raised when the user does not have permission to access the requested resource."""


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
