from . import routes_utils as utils
import requests
import logging
from flask import Blueprint, jsonify, current_app, render_template, session

requests_bp = Blueprint("requests", __name__, url_prefix="/requests")


@requests_bp.before_request
def update_role():
    utils.update_role()


@requests_bp.route("", methods=["GET"])
def dashboard():
    username = session.get("username")
    role = session.get("role")
    return render_template("requests_page.html", username=username, role=role)


@requests_bp.route("/books/pending", methods=["GET"])
def get_pending_books():
    try:
        books_data = utils.make_authenticated_get_request(
            f"{current_app.config['BOOKS_SERVICE_URL']}/books/pending"
        )

        # filter out books that are created by the current user
        books_data = [
            item
            for item in books_data
            if not (
                isinstance(item.get("user"), dict)
                and item["user"].get("keycloakId") == session.get("keycloak_user_id")
            )
        ]

        return jsonify(books_data)
    except utils.NoPermissionError:
        return (
            jsonify({"error": "You do not have permission to access this resource."}),
            403,
        )
    except requests.exceptions.RequestException as e:
        logging.error(f"Error connecting to books service: {e}")
        return jsonify({"error": "Error fetching books data."}), 500


@requests_bp.route("/reviews/pending", methods=["GET"])
def get_pending_reviews():
    try:
        reviews_data = utils.make_authenticated_get_request(
            f"{current_app.config['BOOKS_SERVICE_URL']}/reviews/pending"
        )

        # filter out reviews that are created by the current user
        reviews_data = [
            item
            for item in reviews_data
            if not (
                isinstance(item.get("user"), dict)
                and item["user"].get("keycloakId") == session.get("keycloak_user_id")
            )
        ]

        return jsonify(reviews_data)
    except utils.NoPermissionError:
        return (
            jsonify({"error": "You do not have permission to access this resource."}),
            403,
        )
    except requests.exceptions.RequestException as e:
        logging.error(f"Error connecting to books service: {e}")
        return jsonify({"error": "Error fetching reviews data."}), 500


@requests_bp.route("/books/approve/<id>", methods=["GET"])
def approve_book(id):
    try:
        response = utils.make_authenticated_get_request(
            f"{current_app.config['BOOKS_SERVICE_URL']}/books/approve/{id}",
        )
        return jsonify(response)
    except utils.NoPermissionError:
        return (
            jsonify({"error": "You do not have permission to access this resource."}),
            403,
        )
    except requests.exceptions.RequestException as e:
        logging.error(f"Error connecting to books service: {e}")
        return jsonify({"error": "Error approving book."}), 500


@requests_bp.route("/books/reject/<id>", methods=["GET"])
def reject_book(id):
    try:
        response = utils.make_authenticated_get_request(
            f"{current_app.config['BOOKS_SERVICE_URL']}/books/reject/{id}",
        )
        return jsonify(response)
    except utils.NoPermissionError:
        return (
            jsonify({"error": "You do not have permission to access this resource."}),
            403,
        )
    except requests.exceptions.RequestException as e:
        logging.error(f"Error connecting to books service: {e}")
        return jsonify({"error": "Error rejecting book."}), 500


@requests_bp.route("/reviews/approve/<id>", methods=["GET"])
def approve_review(id):
    try:
        response = utils.make_authenticated_get_request(
            f"{current_app.config['BOOKS_SERVICE_URL']}/reviews/approve/{id}",
        )
        return jsonify(response)
    except utils.NoPermissionError:
        return (
            jsonify({"error": "You do not have permission to access this resource."}),
            403,
        )
    except requests.exceptions.RequestException as e:
        logging.error(f"Error connecting to books service: {e}")
        return jsonify({"error": "Error approving review."}), 500


@requests_bp.route("/reviews/reject/<id>", methods=["GET"])
def reject_review(id):
    try:
        response = utils.make_authenticated_get_request(
            f"{current_app.config['BOOKS_SERVICE_URL']}/reviews/reject/{id}",
        )
        return jsonify(response)
    except utils.NoPermissionError:
        return (
            jsonify({"error": "You do not have permission to access this resource."}),
            403,
        )
    except requests.exceptions.RequestException as e:
        logging.error(f"Error connecting to books service: {e}")
        return jsonify({"error": "Error rejecting review."}), 500
