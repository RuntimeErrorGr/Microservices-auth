import logging
import sys
import os
from flask import Flask, session, request, jsonify
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
        # Add JWT token from session to request headers
        if 'Authorization' in session:
            request.environ['HTTP_AUTHORIZATION'] = f"Bearer {session['Authorization']}"
        
        # Debug logging
        app.logger.debug("=== Request Debug Info ===")
        app.logger.debug(f"Request Path: {request.path}")
        app.logger.debug(f"Request Method: {request.method}")
        app.logger.debug(f"Request Headers: {dict(request.headers)}")
        app.logger.debug(f"Authorization Header Present: {'Authorization' in request.headers}")
        app.logger.debug(f"Session Authorization Present: {'Authorization' in session}")
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            app.logger.debug(f"Auth Header (truncated): {auth_header[:50]}...")
        if 'Authorization' in session:
            session_auth = session['Authorization']
            app.logger.debug(f"Session Auth (truncated): {session_auth[:50]}...")
        
        app.logger.debug("=== End Request Debug Info ===")

    @app.route('/debug/auth-headers')
    def debug_auth_headers():
        return jsonify({
            'headers': dict(request.headers),
            'session_auth': session.get('Authorization'),
            'environ_auth': request.environ.get('HTTP_AUTHORIZATION'),
            'all_environ': {k:v for k,v in request.environ.items() if isinstance(v, str) and k.startswith('HTTP_')},
            'session': {k:v for k,v in session.items() if k != '_permanent'},
            'auth_debug': {
                'headers_auth_present': 'Authorization' in request.headers,
                'session_auth_present': 'Authorization' in session,
                'environ_auth_present': 'HTTP_AUTHORIZATION' in request.environ
            }
        })

    @app.route('/debug/request-info')
    def debug_request_info():
        return jsonify({
            'path': request.path,
            'method': request.method,
            'headers': dict(request.headers),
            'auth_present': 'Authorization' in request.headers,
            'session': {k: v for k, v in session.items() if k != '_permanent'},
            'environ': {k: str(v) for k, v in request.environ.items() 
                       if isinstance(v, (str, int, float, bool, list, dict))}
        })

    @app.after_request
    def after_request(response):
        # Log response status
        app.logger.debug(f"Response Status: {response.status_code}")
        return response

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