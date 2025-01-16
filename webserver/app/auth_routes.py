from flask import (
    Blueprint,
    request,
    session,
    current_app,
    jsonify,
    redirect,
    url_for,
    render_template,
)
import requests
import logging
import jwt
from . import routes_utils as utils
from datetime import timedelta

auth_bp = Blueprint("auth", __name__)

@auth_bp.before_request
def before_request():
    session.permanent = True
    current_app.permanent_session_lifetime = timedelta(hours=1)
    
    # Forward the token to Istio
    if 'Authorization' in session:
        token = session['Authorization']
        request.environ['HTTP_AUTHORIZATION'] = f"Bearer {token}"

@auth_bp.route("/", methods=["GET"])
def index():
    if session.get("Authorization"):
        try:
            token = session.get("Authorization")
            decoded_token = jwt.decode(token, options={"verify_signature": False})
            logging.info("User already logged in")
            return redirect(url_for("auth.dashboard"))
        except jwt.PyJWTError:
            session.clear()
            logging.info("Invalid token, clearing session")
    logging.info("User not logged in")
    return render_template("index.html")

@auth_bp.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    
    logging.info("Login attempt for user: %s", username)

    data = f"client_id=Istio&username={username}&password={password}&grant_type=password"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': '*/*',
    }

    try:
        response = requests.post(
            current_app.config["KEYCLOAK_REALM_ISTIO_OPENID_TOKEN_URL"],
            data=data,
            headers=headers,
            verify=False,
            timeout=5
        )
        
        logging.info("Keycloak response code: %d", response.status_code)

        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data["access_token"]
            
            session["Authorization"] = access_token
            session["istio_token"] = f"Bearer {access_token}"
            session["refresh_token"] = token_data["refresh_token"]
            session["username"] = username

            try:
                decoded_token = jwt.decode(access_token, options={"verify_signature": False})
                
                realm_roles = decoded_token.get('realm_access', {}).get('roles', [])
                resource_roles = decoded_token.get('resource_access', {}).get('Istio', {}).get('roles', [])
                
                all_roles = list(set(realm_roles + resource_roles))
                
                session["user_roles"] = all_roles
                session["role"] = "-".join(all_roles)
                session["resource_access"] = {
                    "Istio": {
                        "roles": resource_roles
                    }
                }
                session["realm_access"] = {
                    "roles": realm_roles
                }

                request.environ['HTTP_AUTHORIZATION'] = f"Bearer {access_token}"

                logging.info(f"Login successful for {username}")
                logging.info(f"All roles: {all_roles}")
                logging.info(f"Realm roles: {realm_roles}")
                logging.info(f"Resource roles: {resource_roles}")
                
                return jsonify({"success": True, "redirect": url_for("auth.dashboard")})
            
            except jwt.PyJWTError as jwt_error:
                logging.error(f"JWT decoding error: {jwt_error}")
                session.clear()
                return jsonify({"success": False, "message": "Invalid token"}), 401

        else:
            logging.error("Login failed with status %s: %s", response.status_code, response.text)
            session.clear()
            return jsonify({"success": False, "message": "Invalid credentials"}), 401

    except requests.exceptions.RequestException as e:
        logging.error("Request exception during login: %s", str(e))
        session.clear()
        return jsonify({"success": False, "message": "Invalid credentials"}), 401

@auth_bp.route("/dashboard", methods=["GET"])
def dashboard():
    access_token = session.get("Authorization")
    if not access_token:
        logging.error("User not logged in")
        return redirect(url_for("auth.index"))

    try:
        decoded_token = jwt.decode(access_token, options={"verify_signature": False})
        logging.info("User logged in")
        return render_template(
            "dashboard.html", 
            username=session.get("username"), 
            role=session.get("role")
        )
    except jwt.PyJWTError:
        logging.error("Invalid token")
        session.clear()
        return redirect(url_for("auth.index"))

@auth_bp.route('/debug/session', methods=['GET'])
def debug_session():
    try:
        token = session.get('Authorization')
        
        if not token:
            return jsonify({'error': 'No authorization token found'}), 401
        
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        
        return jsonify({
            'username': session.get('username'),
            'decoded_token': decoded_token,
            'roles': {
                'realm_access': decoded_token.get('realm_access', {}),
                'resource_access': decoded_token.get('resource_access', {}),
                'user_roles': session.get('user_roles')
            },
            'session_data': {
                'role': session.get('role'),
                'token_expiry': session.get('token_expiry')
            }
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'session_contents': dict(session)
        }), 500

@auth_bp.route('/debug/token-check')
def token_check():
    return jsonify({
        'headers': {k:v for k,v in request.headers.items()},
        'environ': {k:v for k,v in request.environ.items() if k.startswith('HTTP_')},
        'session': {k:v for k,v in session.items() if k != '_permanent'},
        'auth_debug': {
            'auth_header_present': 'Authorization' in request.headers,
            'auth_environ_present': 'HTTP_AUTHORIZATION' in request.environ,
            'auth_session_present': 'Authorization' in session
        }
    })

@auth_bp.route("/logout", methods=["POST"])
def logout():
    access_token = session.get("Authorization")
    if not access_token:
        return jsonify({"success": False, "message": "No active session"}), 400

    data = {
        "client_id": utils.ISTIO_CLIENT_ID,
        "refresh_token": session.get("refresh_token"),
    }
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    try:
        response = requests.post(
            current_app.config["KEYCLOAK_REALM_ISTIO_OPENID_LOGOUT_URL"],
            data=data,
            headers=headers,
            verify=False,
        )
        if response.status_code in [200, 201, 202, 203, 204]:
            session.clear()
            return jsonify({"success": True, "redirect": url_for("auth.index")})
        else:
            logging.error(f"Logout failed: {response.text}")
            return (
                jsonify({"success": False, "message": "Logout failed"}),
                response.status_code,
            )
    except requests.exceptions.RequestException as e:
        logging.error(f"Error during logout: {e}")
        return jsonify({"success": False, "message": "Error during logout"}), 500