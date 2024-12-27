from flask import Blueprint, jsonify, current_app, render_template, session
import requests
import logging

books_info_bp = Blueprint("books", __name__)


@books_info_bp.route("/books", methods=["GET"])
def index():
    try:
        books_service_url = current_app.config["BOOKS_SERVICE_URL"]
        response = requests.get(f"{books_service_url}/books", timeout=5)

        if response.status_code == 200:
            books_data = response.json()
            logging.info(f"Fetched books data: {books_data}")
            return jsonify(books_data)
        else:
            logging.error(
                f"Failed to fetch books: {response.status_code} {response.text}"
            )
            return (
                jsonify({"error": "Failed to fetch books data."}),
                response.status_code,
            )

    except requests.exceptions.RequestException as e:
        logging.error(f"Error connecting to books service: {e}")
        return jsonify({"error": "Error fetching books data."}), 500


@books_info_bp.route("/books/<isbn>", methods=["GET"])
def get_book(isbn):
    try:
        books_service_url = current_app.config["BOOKS_SERVICE_URL"]
        response = requests.get(f"{books_service_url}/books/{isbn}", timeout=5)
        username = session.get("username")
        role = session.get("role")
        if response.status_code == 200:
            book_data = response.json()
            logging.info(f"Fetched book data: {book_data}")
            return render_template(
                "book_page.html", book=book_data, username=username, role=role
            )
        else:
            logging.error(
                f"Failed to fetch book: {response.status_code} {response.text}"
            )
            return (
                jsonify({"error": "Failed to fetch book data."}),
                response.status_code,
            )

    except requests.exceptions.RequestException as e:
        logging.error(f"Error connecting to books service: {e}")
        return jsonify({"error": "Error fetching book data."}), 500
