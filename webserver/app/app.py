import logging
import sys
import os
from flask import Flask, session
from datetime import timedelta
from .config import Config
from .routes_utils import get_user_roles
from .auth_routes import auth_bp
from .books_info_routes import books_info_bp
from .requests_routes import requests_bp
from .policy_route import policy_blueprint

__all__ = ["create_app"]

def create_app():
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "templates"))
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "static"))
    app = Flask(
        Config.PROJECT_NAME,
        instance_relative_config=True,
        template_folder=template_dir,
        static_folder=static_dir,
    )
    
    # Configure session handling
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config["SESSION_TYPE"] = "filesystem"

    configure_logging()
    configure_app(app)
    configure_blueprints(app)

    @app.before_request
    def before_request():
        session.permanent = True

    logging.info("Flask Webserver started")

    return app


def configure_app(app: Flask):
    app.config.from_object(Config)


def configure_blueprints(app: Flask):
    app.register_blueprint(auth_bp)
    app.register_blueprint(books_info_bp)
    app.register_blueprint(requests_bp)
    app.register_blueprint(policy_blueprint)


def configure_logging():
    log_handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)-8s %(filename)s %(funcName)s %(lineno)d  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    log_handler.setFormatter(formatter)
    log_handler.setLevel(logging.DEBUG)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(log_handler)

    logging.info("Logging configured")