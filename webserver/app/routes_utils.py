import logging
import requests
from flask import session, current_app


class NoPermissionError(Exception):
    """Raised when the user does not have permission to access the requested resource."""


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
