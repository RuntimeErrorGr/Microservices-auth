from dataclasses import dataclass
import os


# Only load .env in non-Kubernetes environments
if os.getenv("KUBERNETES_SERVICE_HOST") is None:
    from dotenv import load_dotenv

    basedir = os.path.abspath(os.path.dirname(__file__))
    load_dotenv(os.path.join(basedir, ".env"))


@dataclass
class Config:
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "webserver")
    PROJECT_ROOT: str = os.path.abspath(os.path.dirname(__file__))
    FLASK_DEBUG: bool = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    KEYCLOAK_URL: str = os.getenv("KEYCLOAK_URL")
    BOOKS_SERVICE_URL: str = os.getenv("BOOKS_SERVICE_URL")
