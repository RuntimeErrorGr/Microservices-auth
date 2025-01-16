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
        
        base_permissions = []
        for role in ['user', 'verified', 'moderator']:
            for permission in ['view', 'add', 'delete']:
                base_permissions.append({
                    'role': role,
                    'permission': permission,
                    'granted': False
                })

        books_permissions = base_permissions.copy()
        reviews_permissions = base_permissions.copy()
        
        try:
            books_policy = custom_api.get_namespaced_custom_object(
                group="security.istio.io",
                version="v1beta1",
                namespace="default",
                plural="authorizationpolicies",
                name="books-policy"
            )
            
            if books_policy.get('spec', {}).get('rules'):
                for rule in books_policy['spec']['rules']:
                    if 'when' in rule:
                        role = rule['when'][0]['values'][0]
                        methods = rule['to'][0]['operation'].get('methods', [])
                        
                        for perm in books_permissions:
                            if perm['role'] == role:
                                if 'GET' in methods and perm['permission'] == 'view':
                                    perm['granted'] = True
                                if 'POST' in methods and perm['permission'] == 'add':
                                    perm['granted'] = True
                                if 'DELETE' in methods and perm['permission'] == 'delete':
                                    perm['granted'] = True

        except client.rest.ApiException as e:
            if e.status != 404:
                raise
        
        try:
            reviews_policy = custom_api.get_namespaced_custom_object(
                group="security.istio.io",
                version="v1beta1",
                namespace="default",
                plural="authorizationpolicies",
                name="reviews-policy"
            )
            
            if reviews_policy.get('spec', {}).get('rules'):
                for rule in reviews_policy['spec']['rules']:
                    if 'when' in rule:
                        role = rule['when'][0]['values'][0]
                        methods = rule['to'][0]['operation'].get('methods', [])
                        
                        for perm in reviews_permissions:
                            if perm['role'] == role:
                                if 'GET' in methods and perm['permission'] == 'view':
                                    perm['granted'] = True
                                if 'POST' in methods and perm['permission'] == 'add':
                                    perm['granted'] = True
                                if 'DELETE' in methods and perm['permission'] == 'delete':
                                    perm['granted'] = True

        except client.rest.ApiException as e:
            if e.status != 404:
                raise

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
    try:
        config.load_incluster_config()
        custom_api = client.CustomObjectsApi()
        app_label = "books-information"
        
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
                'action': 'ALLOW',
                'rules': []
            }
        }

        granted_permissions = [p for p in permissions if p['granted']]
        if granted_permissions:
            allow_rules = []
            for role in ['user', 'verified', 'moderator']:
                role_permissions = [p for p in granted_permissions if p['role'] == role]
                if role_permissions:
                    methods = []
                    paths = []
                    for perm in role_permissions:
                        if resource == 'books':
                            if perm['permission'] == 'view':
                                methods.append('GET')
                                paths.extend([
                                    '/books/approved',
                                    '/books/title/*',
                                    '/books/ratings/*',
                                    '/books/*'
                                ])
                            elif perm['permission'] == 'add':
                                methods.append('POST')
                                paths.extend([
                                    '/books/add',
                                    '/books/pending'
                                ])
                            elif perm['permission'] == 'delete':
                                methods.append('DELETE')
                                paths.extend([
                                    '/books/delete/*'
                                ])
                        else:  # reviews
                            if perm['permission'] == 'view':
                                methods.append('GET')
                                paths.extend([
                                    '/reviews/by-isbn/*',
                                    '/reviews/pending'
                                ])
                            elif perm['permission'] == 'add':
                                methods.append('POST')
                                paths.append('/reviews/add')
                            elif perm['permission'] == 'delete':
                                methods.extend(['DELETE'])
                                paths.extend([
                                    '/reviews/delete/*',
                                    '/reviews/approve/*',
                                    '/reviews/reject/*'
                                ])
                    
                    if methods and paths:
                        allow_rules.append({
                            'to': [{
                                'operation': {
                                    'methods': list(set(methods)),
                                    'paths': list(set(paths))
                                }
                            }],
                            'when': [{
                                'key': 'request.auth.claims[resource_access][Istio][roles]',
                                'values': [role]
                            }]
                        })
            
            if allow_rules:
                policy['spec']['action'] = 'ALLOW'
                policy['spec']['rules'] = allow_rules

        try:
            existing_policy = custom_api.get_namespaced_custom_object(
                group="security.istio.io",
                version="v1beta1",
                namespace="default",
                plural="authorizationpolicies",
                name=f"{resource}-policy"
            )
            policy['metadata']['resourceVersion'] = existing_policy['metadata']['resourceVersion']
        except client.rest.ApiException as e:
            if e.status != 404:
                raise

        return policy

    except Exception as e:
        current_app.logger.error(f"Error creating policy: {str(e)}")
        raise

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
            try:
                existing_policy = custom_api.get_namespaced_custom_object(
                    group="security.istio.io",
                    version="v1beta1",
                    namespace="default",
                    plural="authorizationpolicies",
                    name=f"{resource}-policy"
                )
                updated_policy = custom_api.replace_namespaced_custom_object(
                    group="security.istio.io",
                    version="v1beta1",
                    namespace="default",
                    plural="authorizationpolicies",
                    name=f"{resource}-policy",
                    body=policy
                )
                current_app.logger.info(f"Updated {resource} policy: {updated_policy}")
            except client.rest.ApiException as e:
                if e.status == 404:
                    new_policy = custom_api.create_namespaced_custom_object(
                        group="security.istio.io",
                        version="v1beta1",
                        namespace="default",
                        plural="authorizationpolicies",
                        body=policy
                    )
                    current_app.logger.info(f"Created new {resource} policy: {new_policy}")
                else:
                    raise
            
            return jsonify({'success': True})
            
        except client.rest.ApiException as e:
            current_app.logger.error(f"Kubernetes API error: {str(e)}")
            return jsonify({'error': str(e)}), e.status
            
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
    try:
        config.load_incluster_config()
        custom_api = client.CustomObjectsApi()
        
        policies = custom_api.list_namespaced_custom_object(
            group="security.istio.io",
            version="v1beta1",
            namespace="default",
            plural="authorizationpolicies"
        )
        
        token = session.get('Authorization')
        decoded = jwt.decode(token, options={"verify_signature": False}) if token else None
        
        return jsonify({
            'policies': policies,
            'token_info': {
                'token_exists': bool(token),
                'token_decoded': decoded,
                'session_roles': session.get('user_roles'),
                'session_role': session.get('role')
            },
            'service_info': {
                'books_url': current_app.config.get("BOOKS_SERVICE_URL"),
                'reviews_url': current_app.config.get("REVIEWS_SERVICE_URL")
            }
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