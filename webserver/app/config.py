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
    KEYCLOAK_REALM_ISTIO_URL = KEYCLOAK_URL + "/realms/Istio"
    KEYCLOAK_REALM_MASTER_URL = KEYCLOAK_URL + "/realms/master"
    KEYCLOAK_REALM_ISTIO_OPENID_URL = (
        KEYCLOAK_REALM_ISTIO_URL + "/protocol/openid-connect"
    )
    KEYCLOAK_REALM_MASTER_OPENID_URL = (
        KEYCLOAK_REALM_MASTER_URL + "/protocol/openid-connect"
    )
    KEYCLOAK_REALM_ISTIO_OPENID_TOKEN_URL = KEYCLOAK_REALM_ISTIO_OPENID_URL + "/token"
    KEYCLOAK_REALM_ISTIO_OPENID_LOGOUT_URL = KEYCLOAK_REALM_ISTIO_OPENID_URL + "/logout"
    KEYCLOAK_REALM_MASTER_OPENID_TOKEN_URL = KEYCLOAK_REALM_MASTER_OPENID_URL + "/token"
    KEYCLAOK_REALM_MASTER_OPENID_LOGOUT_URL = (
        KEYCLOAK_REALM_MASTER_OPENID_URL + "/logout"
    )
    KEYCLOAK_USERS_URL = KEYCLOAK_URL + "/admin/realms/Istio/users"
    KEYCLOAK_CLIENTS_URL = KEYCLOAK_URL + "/admin/realms/Istio/clients"
    BOOKS_SERVICE_URL: str = os.getenv("BOOKS_SERVICE_URL")
