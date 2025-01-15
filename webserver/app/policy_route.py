import jwt
import logging
from functools import wraps
from flask import (
    Blueprint, 
    jsonify, 
    request, 
    render_template, 
    session, 
    current_app,
    redirect,
    url_for
)
from kubernetes import client, config

policy_blueprint = Blueprint('policy', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_app.logger.error("=" * 50)
        current_app.logger.error("ADMIN ACCESS ATTEMPT")
        
        if not session.get('Authorization'):
            current_app.logger.error("No Authorization token in session")
            return redirect(url_for('auth.login'))

        try:
            token = session.get('Authorization')
            decoded_token = jwt.decode(token, options={"verify_signature": False})
            
            is_admin = False
            
            resource_roles = decoded_token.get('resource_access', {}).get('Istio', {}).get('roles', [])
            if 'admin' in resource_roles:
                is_admin = True
            
            realm_roles = decoded_token.get('realm_access', {}).get('roles', [])
            if 'admin' in realm_roles:
                is_admin = True
                
            if not session.get('user_roles'):
                session['user_roles'] = list(set(resource_roles + realm_roles))
                
            if not is_admin:
                current_app.logger.error(f"User {session.get('username')} is not admin")
                return redirect(url_for('auth.dashboard'))

            return f(*args, **kwargs)
            
        except Exception as e:
            current_app.logger.error(f"Error checking admin status: {str(e)}")
            session.clear()
            return redirect(url_for('auth.login'))
            
    return decorated_function

@policy_blueprint.route('/policy/editor')
@admin_required
def editor():
    current_app.logger.error("=" * 50)
    current_app.logger.error("POLICY EDITOR ROUTE ACCESSED")
    
    current_app.logger.error(f"Request headers: {dict(request.headers)}")
    current_app.logger.error(f"Authorization header: {request.headers.get('Authorization')}")
    
    current_app.logger.error(f"Session data: {dict(session)}")
    token = session.get('Authorization')
    
    if token:
        try:
            decoded = jwt.decode(token, options={"verify_signature": False})
            current_app.logger.error(f"Decoded token: {decoded}")
            current_app.logger.error(f"Resource access: {decoded.get('resource_access')}")
            current_app.logger.error(f"Realm access: {decoded.get('realm_access')}")
            current_app.logger.error(f"Groups: {decoded.get('groups')}")
        except Exception as e:
            current_app.logger.error(f"Error decoding token: {e}")
    
    return render_template('policy_editor.html')

@policy_blueprint.route('/debug/auth-test')
def debug_auth_test():
    token = session.get('Authorization')
    headers = {
        'Authorization': f'Bearer {token}'
    }
    return jsonify({
        'headers': dict(request.headers),
        'session': dict(session),
        'auth_header': headers.get('Authorization'),
        'token_data': jwt.decode(token, options={"verify_signature": False}) if token else None
    })

def get_policy_permissions(custom_api, resource_name):
    """Helper function to fetch and parse permissions from a policy"""
    permissions = []
    try:
        policy = custom_api.get_namespaced_custom_object(
            group="security.istio.io",
            version="v1beta1",
            namespace="default",
            plural="authorizationpolicies",
            name=f"{resource_name}-policy"
        )
        
        current_app.logger.info(f"Retrieved {resource_name} policy: {policy}")
        
        for rule in policy['spec'].get('rules', []):
            if 'from' in rule and 'to' in rule:
                principal = rule['from'][0]['source']['principals'][0]
                role = principal.split('/')[-1]
                
                methods = rule['to'][0]['operation'].get('methods', [])
                for method in methods:
                    permission = {
                        'role': role,
                        'permission': 'view' if method == 'GET' else 
                                    'add' if method == 'POST' else 
                                    'delete' if method == 'DELETE' else None,
                        'granted': True
                    }
                    if permission['permission']:
                        permissions.append(permission)
                        
    except client.rest.ApiException as e:
        if e.status != 404:
            raise
        current_app.logger.warning(f"{resource_name} policy not found")
    
    return permissions

@policy_blueprint.route('/api/permissions', methods=['GET'])
@admin_required
def get_permissions():
    try:
        config.load_incluster_config()
        custom_api = client.CustomObjectsApi()
        
        books_permissions = get_policy_permissions(custom_api, 'books')
        reviews_permissions = get_policy_permissions(custom_api, 'reviews')
        
        current_app.logger.info(f"Fetched books permissions: {books_permissions}")
        current_app.logger.info(f"Fetched reviews permissions: {reviews_permissions}")
        
        return jsonify({
            'books_permissions': books_permissions,
            'reviews_permissions': reviews_permissions
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting permissions: {str(e)}")
        return jsonify({'error': str(e)}), 500

def create_authorization_policy(resource, permissions):
    """Create Istio Authorization Policy based on permissions"""
    rules = []
    app_label = "books-information" if resource == "books" else "webserver"
    
    for role in ['user', 'verified', 'moderator']:
        role_permissions = [p for p in permissions if p['role'] == role and p['granted']]
        
        if role_permissions:
            methods = []
            
            for perm in role_permissions:
                if perm['permission'] == 'view':
                    methods.append('GET')
                elif perm['permission'] == 'add':
                    methods.append('POST')
                elif perm['permission'] == 'delete':
                    methods.append('DELETE')

            if methods:
                rule = {
                    'from': [{
                        'source': {
                            'principals': [f"cluster.local/ns/default/sa/{role}"]
                        }
                    }],
                    'to': [{
                        'operation': {
                            'methods': methods,
                            'paths': ['/books*'] if resource == 'books' else ['/books/*/reviews*']
                        }
                    }]
                }
                rules.append(rule)

    policy = {
        'apiVersion': 'security.istio.io/v1beta1',
        'kind': 'AuthorizationPolicy',
        'metadata': {
            'name': f"{resource}-policy",
            'namespace': 'default'
        },
        'spec': {
            'selector': {
                'matchLabels': {
                    'app': app_label
                }
            },
            'rules': rules
        }
    }

    return policy

@policy_blueprint.route('/api/permissions/<resource>', methods=['POST'])
@admin_required
def update_resource_permissions(resource):
    try:
        config.load_incluster_config()
        custom_api = client.CustomObjectsApi()
        
        permissions = request.json.get('permissions', [])
        current_app.logger.info(f"Updating {resource} permissions: {permissions}")
        
        policy = create_authorization_policy(resource, permissions)
        
        try:
            custom_api.replace_namespaced_custom_object(
                group="security.istio.io",
                version="v1beta1",
                namespace="default",
                plural="authorizationpolicies",
                name=f"{resource}-policy",
                body=policy
            )
            current_app.logger.info(f"Updated {resource} policy")
        except client.rest.ApiException as e:
            if e.status == 404:
                custom_api.create_namespaced_custom_object(
                    group="security.istio.io",
                    version="v1beta1",
                    namespace="default",
                    plural="authorizationpolicies",
                    body=policy
                )
                current_app.logger.info(f"Created new {resource} policy")
            else:
                raise
        
        return jsonify({'success': True})
        
    except Exception as e:
        current_app.logger.error(f"Error updating permissions: {str(e)}")
        return jsonify({'error': str(e)}), 500

@policy_blueprint.route('/debug/admin-check')
def comprehensive_admin_check():
    """Debug route for admin access"""
    try:
        token = session.get('Authorization')
        
        if not token:
            return jsonify({
                'error': 'No authorization token found',
                'session_contents': dict(session),
                'session_keys': list(session.keys())
            }), 401
        
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        
        role_sources = {
            'realm_access': decoded_token.get('realm_access', {}),
            'resource_access': decoded_token.get('resource_access', {}),
            'session_user_roles': session.get('user_roles'),
            'full_token': decoded_token
        }
        
        role_check_details = {
            'realm_roles': role_sources['realm_access'].get('roles', []),
            'resource_roles': role_sources['resource_access'].get('Istio', {}).get('roles', []),
            'session_roles': role_sources['session_user_roles'] or []
        }
        
        admin_status = {
            'is_admin': 'admin' in (
                role_check_details['realm_roles'] +
                role_check_details['resource_roles'] +
                role_check_details['session_roles']
            ),
            'role_checking_paths': {
                'realm_access_path': 'decoded_token.realm_access.roles',
                'resource_access_path': 'decoded_token.resource_access.Istio.roles',
                'session_roles_path': 'session.user_roles'
            },
            'role_check_details': role_check_details
        }
        
        return jsonify(admin_status)
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'session_contents': dict(session)
        }), 500

@policy_blueprint.route('/debug/policy-access')
def debug_policy_access():
    token = session.get('Authorization')
    if not token:
        return jsonify({'error': 'No token'}), 401
    
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        return jsonify({
            'token_info': {
                'resource_access': decoded.get('resource_access', {}),
                'realm_access': decoded.get('realm_access', {}),
                'roles': session.get('user_roles', []),
                'role': session.get('role'),
            },
            'session_data': dict(session)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@policy_blueprint.route('/debug/token-check')
def debug_token_check():
    current_app.logger.error("=" * 50)
    current_app.logger.error("TOKEN CHECK DEBUG")
    
    token = session.get('Authorization')
    
    try:
        current_app.logger.error(f"Request Headers: {dict(request.headers)}")
        
        if token:
            decoded = jwt.decode(token, options={"verify_signature": False})
            return jsonify({
                'token_first_part': token[:50] + '...',
                'decoded': {
                    'resource_access': decoded.get('resource_access'),
                    'realm_access': decoded.get('realm_access'),
                    'preferred_username': decoded.get('preferred_username'),
                    'exp': decoded.get('exp'),
                    'iss': decoded.get('iss')
                },
                'headers': dict(request.headers),
                'session_data': {
                    'username': session.get('username'),
                    'role': session.get('role'),
                    'user_roles': session.get('user_roles')
                }
            })
        return jsonify({'error': 'No token found'})
    except Exception as e:
        current_app.logger.error(f"Error in debug endpoint: {str(e)}")
        return jsonify({'error': str(e)})

# @policy_blueprint.route('/debug/full-auth')
# def debug_full_auth():
#     token = session.get('Authorization')
#     headers = {k: v for k, v in request.headers.items()}
    
#     try:
#         decoded = jwt.decode(token, options={"verify_signature": False})
#         return jsonify({
#             'headers': headers,
#             'token': {
#                 'raw': token[:50] + '...',
#                 'decoded': decoded,
#                 'claims': {
#                     'resource_access': decoded.get('resource_access'),
#                     'preferred_username': decoded.get('preferred_username'),
#                     'roles': decoded.get('resource_access', {}).get('Istio', {}).get('roles', [])
#                 }
#             },
#             'session': {
#                 'username': session.get('username'),
#                 'roles': session.get('user_roles'),
#                 'role': session.get('role')
#             }
#         })
#     except Exception as e:
#         return jsonify({'error': str(e)})