from flask import Blueprint, jsonify, request, render_template, session, current_app
from functools import wraps
from kubernetes import client, config
import logging

policy_blueprint = Blueprint('policy', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_app.logger.info(f"Checking admin access")
        current_app.logger.info(f"User: {session.get('username')}")
        current_app.logger.info(f"User roles: {session.get('user_roles')}")
        
        if 'admin' not in session.get('user_roles', []):
            current_app.logger.error(f"Admin access denied for user {session.get('username')}")
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

@policy_blueprint.route('/policy/editor')
@admin_required
def editor():
    current_app.logger.info(f"Accessing policy editor")
    current_app.logger.info(f"User: {session.get('username')}")
    current_app.logger.info(f"Roles from session: {session.get('user_roles')}")
    current_app.logger.info(f"Session: {session}")
    
    user_roles = session.get('user_roles', [])
    if 'admin' not in user_roles:
        current_app.logger.error(f"Admin access denied. User roles: {user_roles}")
        return jsonify({'error': 'Admin access required'}), 403
    
    return render_template('policy_editor.html')

@policy_blueprint.route('/api/permissions', methods=['GET'])
@admin_required
def get_permissions():
    try:
        config.load_incluster_config()
        custom_api = client.CustomObjectsApi()
        
        # Get current authorization policies
        policies = custom_api.list_namespaced_custom_object(
            group="security.istio.io",
            version="v1beta1",
            namespace="default",
            plural="authorizationpolicies"
        )

        books_permissions = []
        reviews_permissions = []

        for policy in policies['items']:
            if policy['metadata']['name'] == 'books-policy':
                books_permissions = extract_permissions(policy)
            elif policy['metadata']['name'] == 'reviews-policy':
                reviews_permissions = extract_permissions(policy)

        return jsonify({
            'books_permissions': books_permissions,
            'reviews_permissions': reviews_permissions
        })
    except Exception as e:
        logging.error(f"Error getting permissions: {str(e)}")
        return jsonify({'error': str(e)}), 500

@policy_blueprint.route('/api/permissions/<resource>', methods=['POST'])
@admin_required
def update_permissions(resource):
    try:
        permissions = request.json.get('permissions', [])
        
        config.load_incluster_config()
        custom_api = client.CustomObjectsApi()

        # Create authorization policy object
        policy = create_authorization_policy(resource, permissions)

        try:
            # Try to update existing policy
            custom_api.replace_namespaced_custom_object(
                group="security.istio.io",
                version="v1beta1",
                namespace="default",
                plural="authorizationpolicies",
                name=f"{resource}-policy",
                body=policy
            )
        except client.rest.ApiException as e:
            if e.status == 404:
                # Create new policy if it doesn't exist
                custom_api.create_namespaced_custom_object(
                    group="security.istio.io",
                    version="v1beta1",
                    namespace="default",
                    plural="authorizationpolicies",
                    body=policy
                )
            else:
                raise

        return jsonify({'success': True})
    except Exception as e:
        logging.error(f"Error updating permissions: {str(e)}")
        return jsonify({'error': str(e)}), 500

def create_authorization_policy(resource, permissions):
    rules = []
    app_label = "books-information" if resource == "books" else "webserver"
    
    for role in ['user', 'verified', 'moderator']:
        role_permissions = [p for p in permissions if p['role'] == role and p['granted']]
        
        if role_permissions:
            methods = []
            paths = []
            
            for perm in role_permissions:
                if perm['permission'] == 'view':
                    methods.append('GET')
                elif perm['permission'] == 'add':
                    methods.append('POST')
                elif perm['permission'] == 'delete':
                    methods.append('DELETE')

            # Handle paths based on resource type
            if resource == 'books':
                paths = ['/books*']
            else:  # reviews
                paths = ['/books/*/reviews*']

            if methods:
                rules.append({
                    'from': [{
                        'source': {
                            'principals': [f"cluster.local/ns/default/sa/{role}"]
                        }
                    }],
                    'to': [{
                        'operation': {
                            'methods': methods,
                            'paths': paths
                        }
                    }]
                })

    return {
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

def extract_permissions(policy):
    permissions = []
    
    for rule in policy['spec'].get('rules', []):
        role = rule['from'][0]['source']['principals'][0].split('/')[-1]
        methods = rule['to'][0]['operation'].get('methods', [])
        
        for method in methods:
            permission = 'view' if method == 'GET' else 'add' if method == 'POST' else 'delete'
            permissions.append({
                'role': role,
                'permission': permission,
                'granted': True
            })
            
    return permissions