from functools import wraps
from flask import request, jsonify, g
import firebase_admin
from firebase_admin import auth

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 1. Sad Path: No Header
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'Authorization header is missing'}), 401

        # 2. Sad Path: Malformed Header (Bearer <token>)
        parts = auth_header.split()
        if parts[0].lower() != 'bearer' or len(parts) != 2:
            return jsonify({'error': 'Authorization header must be Bearer token'}), 401

        token = parts[1]

        try:
            # 3. Verify Token with Firebase
            decoded_token = auth.verify_id_token(token)
            
            # 4. Happy Path: Inject UID into context
            g.user_id = decoded_token['uid']
            
        except firebase_admin.auth.ExpiredIdTokenError:
            return jsonify({'error': 'Token expired'}), 401
        except firebase_admin.auth.InvalidIdTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        except Exception as e:
            return jsonify({'error': f'Authentication failed: {str(e)}'}), 401

        return f(*args, **kwargs)
    return decorated_function