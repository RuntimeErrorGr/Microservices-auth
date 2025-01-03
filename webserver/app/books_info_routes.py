import requests
import logging
from flask import Blueprint, jsonify, current_app, render_template, session, request
from datetime import datetime
from . import routes_utils as utils

books_info_bp = Blueprint("books", __name__, url_prefix="/books")


@books_info_bp.route("", methods=["GET", "POST"])
def handle_books():
    if request.method == "GET":
        return get_books()
    elif request.method == "POST":
        return add_book()


def get_books():
    try:
        books_data = utils.make_authenticated_get_request(
            f"{current_app.config['BOOKS_SERVICE_URL']}/books/approved"
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


def add_book():
    data = extract_book_data()
    try:
        response = utils.make_authenticated_post_request(
            f"{current_app.config['BOOKS_SERVICE_URL']}/books/add", data
        )
        return jsonify(response)
    except utils.NoPermissionError:
        return (
            jsonify({"error": "You do not have permission to perform this action."}),
            403,
        )
    except requests.exceptions.RequestException as e:
        logging.error(f"Error connecting to books service: {e}")
        return jsonify({"error": "Error adding book."}), 500


def extract_book_data():
    return {
        "isbn": request.json.get("isbn"),
        "title": request.json.get("title"),
        "author": request.json.get("author"),
        "genre": request.json.get("genre"),
        "description": request.json.get("description"),
        "publicationDate": request.json.get("publicationDate"),
    }


def extract_review_data(isbn):
    return {
        "reviewText": request.json.get("text"),
        "bookIsbn": isbn,
        "keycloakId": session.get("keycloak_user_id"),
    }


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


@books_info_bp.route("/<isbn>", methods=["GET"])
def book_page(isbn):
    username = session.get("username")
    role = session.get("role")
    try:
        response = utils.make_authenticated_get_request(
            f"{current_app.config['BOOKS_SERVICE_URL']}/books/title/{isbn}"
        )
        book_id = list(response.keys())[0]
        title = response[book_id]
        logging.info(f"Fetched title: {title}")
        return render_template(
            "book_page.html",
            title=title,
            isbn=isbn,
            username=username,
            role=role,
            id=book_id,
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
            id=None,
        )


@books_info_bp.route("/details/<isbn>", methods=["GET"])
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


@books_info_bp.route("/reviews/<isbn>", methods=["GET", "POST"])
def book_reviews(isbn):
    if request.method == "GET":
        return get_book_reviews(isbn)
    elif request.method == "POST":
        return add_review(isbn)


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
            f"{current_app.config['BOOKS_SERVICE_URL']}/reviews/by-isbn/approved/{isbn}"
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


def add_review(isbn):
    data = extract_review_data(isbn)
    logging.info(f"Adding review: {data}")
    try:
        response = utils.make_authenticated_post_request(
            f"{current_app.config['BOOKS_SERVICE_URL']}/reviews/add", data
        )
        return jsonify(response)
    except utils.NoPermissionError:
        return (
            jsonify({"error": "You do not have permission to perform this action."}),
            403,
        )
    except requests.exceptions.RequestException as e:
        logging.error(f"Error connecting to books service: {e}")
        return jsonify({"error": "Error adding review."}), 500


@books_info_bp.route("/ratings/<isbn>", methods=["GET"])
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
