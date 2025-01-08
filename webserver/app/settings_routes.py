from . import routes_utils as utils
import logging
from flask import Blueprint, render_template, session, request, jsonify

from .routes_utils import change_role, delete_role

settings_bp = Blueprint("settings", __name__, url_prefix="/settings")


@settings_bp.before_request
def update_role():
    utils.update_role()


@settings_bp.route("", methods=["GET"])
def dashboard():
    admin_token = utils.get_admin_token()
    client_id = utils.get_client_id(admin_token)
    session["users"] = [user.to_dict() for user in utils.get_users(admin_token, client_id)]
    users = session.get("users")
    username = session.get("username")
    role = session.get("role")
    roles = session.get("roles")

    logging.info(f"users: {users}")
    return render_template("settings_page.html", users=users, username=username, role=role, roles=roles)


@settings_bp.route('/change_role', methods=['POST'])
def change_role_route():
    data = request.get_json()
    username = data.get('username')
    role_name = data.get('role')

    success = change_role(username, role_name)

    if success:
        return jsonify({'success': True}), 200
    else:
        return jsonify({'success': False, 'message': 'Failed to change role'}), 400


@settings_bp.route('/delete_role', methods=['DELETE'])
def delete_role_route():
    data = request.get_json()
    username = data.get('username')

    success = delete_role(username)

    if success:
        return jsonify({'success': True}), 200
    else:
        return jsonify({'success': False, 'message': 'Failed to change role'}), 400
