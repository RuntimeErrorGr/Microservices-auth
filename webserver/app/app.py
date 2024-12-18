import logging
import os
from flask import Flask
from .config import Config
import sys

__all__ = ["create_app"]


def create_app():
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "templates"))
    app = Flask(
        Config.PROJECT_NAME,
        instance_relative_config=True,
        template_folder=template_dir,
        static_folder="static",
    )
    configure_logging()
    configure_app(app)

    logging.info("Flask Webserver started")

    return app


def configure_app(app: Flask):
    app.config.from_object(Config)


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
