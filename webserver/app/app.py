import logging
import sys
import os
from flask import Flask
from .config import Config
from .auth_routes import auth_bp

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
    configure_logging()
    configure_app(app)
    configure_blueprints(app)

    logging.info("Flask Webserver started")

    return app


def configure_app(app: Flask):
    app.config.from_object(Config)
    app.config["SESSION_TYPE"] = "filesystem"
    app.config["KEYCLOAK_LOGOUT_URL"] = app.config["KEYCLOAK_URL"].replace(
        "token", "logout"
    )


def configure_blueprints(app: Flask):
    app.register_blueprint(auth_bp)


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
