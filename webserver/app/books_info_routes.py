import requests
import logging
from flask import Blueprint, jsonify, current_app, render_template, session
from datetime import datetime

books_info_bp = Blueprint("books", __name__, url_prefix="/books")


class NoPermissionError(Exception):
    """Raised when the user does not have permission to access the requested resource."""


def make_authenticated_request(url):
    access_token = session.get("Authorization")
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    logging.info("Headers: %s", headers)
    try:
        response = requests.get(url, timeout=5, headers=headers)
        if response.status_code in [401, 403]:
            logging.error(
                f"Failed to fetch data: {response.status_code} {response.text}"
            )
            raise NoPermissionError

        if not response.headers.get("Content-Type") == "application/json":
            return response.text

        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error connecting to books service: {e}")
        return None


@books_info_bp.route("", methods=["GET"])
def index():
    try:
        books_data = make_authenticated_request(
            f"{current_app.config['BOOKS_SERVICE_URL']}/books"
        )
        logging.info(f"Fetched books data: {books_data}")
        return jsonify(books_data)
    except NoPermissionError:
        return (
            jsonify({"error": "You do not have permission to access this resource."}),
            403,
        )
    except requests.exceptions.RequestException as e:
        logging.error(f"Error connecting to books service: {e}")
        return jsonify({"error": "Error fetching books data."}), 500


@books_info_bp.route("/<isbn>", methods=["GET"])
def book_page(isbn):
    username = session.get("username")
    role = session.get("role")
    return render_template("book_page.html", username=username, role=role, isbn=isbn)


@books_info_bp.route("/<isbn>/details", methods=["GET"])
def get_book_details(isbn):
    try:
        book_data = make_authenticated_request(
            f"{current_app.config['BOOKS_SERVICE_URL']}/books/{isbn}"
        )
        logging.info(f"Fetched book data: {book_data}")
        return jsonify(book_data)
    except NoPermissionError:
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
        json_response = make_authenticated_request(
            f"{current_app.config['BOOKS_SERVICE_URL']}/reviews/by-isbn/{isbn}"
        )
        reviews_data = transform_reviews(json_response)
        logging.info(f"Fetched reviews data: {reviews_data}")
        return jsonify(reviews_data)
    except NoPermissionError:
        return (
            jsonify({"error": "You do not have permission to access this resource."}),
            403,
        )
    except requests.exceptions.RequestException as e:
        logging.error(f"Error connecting to books service: {e}")
        return jsonify({"error": "Error fetching reviews data."}), 500
