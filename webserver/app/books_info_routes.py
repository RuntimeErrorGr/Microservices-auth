import requests
import logging
from flask import Blueprint, jsonify, current_app, render_template, session, request
from datetime import datetime
from . import routes_utils as utils

books_info_bp = Blueprint("books", __name__, url_prefix="/books")


@books_info_bp.route("", methods=["GET"])
def index():
    try:
        books_data = utils.make_authenticated_get_request(
            f"{current_app.config['BOOKS_SERVICE_URL']}/books"
        )
        return jsonify(books_data)
    except utils.NoPermissionError:
        return (
            jsonify({"error": "You do not have permission to access this resource."}),
            403,
        )
    except requests.exceptions.RequestException as e:
        logging.error(f"Error connecting to books service: {e}")
        return jsonify({"error": "Error fetching books data."}), 500


@books_info_bp.route("", methods=["POST"])
def add_pending_book():

    data = {
        "isbn": request.json.get("isbn"),
        "title": request.json.get("title"),
        "author": request.json.get("author"),
        "publicationYear": request.json.get("publicationYear"),
    }

    try:
        response = utils.make_authenticated_post_request(
            f"{current_app.config['BOOKS_SERVICE_URL']}/books/add", data
        )
        return jsonify(response)
    except utils.NoPermissionError:
        return (
            jsonify({"error": "You do not have permission to access this resource."}),
            403,
        )
    except requests.exceptions.RequestException as e:
        logging.error(f"Error connecting to books service: {e}")
        return jsonify({"error": "Error adding book."}), 500


@books_info_bp.route("/delete/<id>", methods=["DELETE"])
def delete_book(id):
    try:
        response = utils.make_authenticated_delete_request(
            f"{current_app.config['BOOKS_SERVICE_URL']}/books/delete/{id}"
        )
        return jsonify(response)
    except utils.NoPermissionError:
        return (
            jsonify({"error": "You do not have permission to access this resource."}),
            403,
        )
    except requests.exceptions.RequestException as e:
        logging.error(f"Error connecting to books service: {e}")
        return jsonify({"error": "Error deleting book."}), 500


@books_info_bp.route("/approve/<id>", methods=["GET"])
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


@books_info_bp.route("/reject/<id>", methods=["GET"])
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


@books_info_bp.route("/<isbn>", methods=["GET"])
def book_page(isbn):
    username = session.get("username")
    role = session.get("role")
    try:
        title = utils.make_authenticated_get_request(
            f"{current_app.config['BOOKS_SERVICE_URL']}/books/title/{isbn}"
        )
        logging.info(f"Fetched title: {title}")
        return render_template(
            "book_page.html",
            title=title,
            isbn=isbn,
            username=username,
            role=role,
        )
    except utils.NoPermissionError:
        logging.error(
            "User does not have permission to access the presentation page for %s", isbn
        )
        return render_template(
            "book_page.html",
            title="Loading...",
            isbn=isbn,
            username=username,
            role=role,
        )


@books_info_bp.route("/<isbn>/details", methods=["GET"])
def get_book_details(isbn):
    try:
        book_data = utils.make_authenticated_get_request(
            f"{current_app.config['BOOKS_SERVICE_URL']}/books/{isbn}"
        )
        return jsonify(book_data)
    except utils.NoPermissionError:
        return (
            jsonify({"error": "You do not have permission to access this resource."}),
            403,
        )
    except requests.exceptions.RequestException as e:
        logging.error(f"Error connecting to books service: {e}")
        return jsonify({"error": "Error fetching book data."}), 500


@books_info_bp.route("/<isbn>/reviews", methods=["GET"])
def get_book_reviews(isbn):
    def transform_reviews(input_data):
        transformed_data = [
            {
                "reviewer": review["user"]["username"],
                "text": review["reviewText"],
                "date": datetime.fromisoformat(review["reviewDate"]).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
            }
            for review in input_data
        ]
        return transformed_data

    try:
        json_response = utils.make_authenticated_get_request(
            f"{current_app.config['BOOKS_SERVICE_URL']}/reviews/by-isbn/{isbn}"
        )
        reviews_data = transform_reviews(json_response)
        return jsonify(reviews_data)
    except utils.NoPermissionError:
        return (
            jsonify({"error": "You do not have permission to access this resource."}),
            403,
        )
    except requests.exceptions.RequestException as e:
        logging.error(f"Error connecting to books service: {e}")
        return jsonify({"error": "Error fetching reviews data."}), 500


@books_info_bp.route("/<isbn>/ratings", methods=["GET"])
def get_book_ratings(isbn):
    try:
        ratings_data = utils.make_authenticated_get_request(
            f"{current_app.config['BOOKS_SERVICE_URL']}/books/ratings/{isbn}"
        )
        return jsonify(ratings_data)
    except utils.NoPermissionError:
        return (
            jsonify({"error": "You do not have permission to access this resource."}),
            403,
        )
    except requests.exceptions.RequestException as e:
        logging.error(f"Error connecting to books service: {e}")
        return jsonify({"error": "Error fetching ratings data."}), 500
