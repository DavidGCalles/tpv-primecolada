# primecolada-backend/auth_middleware.py

from functools import wraps
from flask import request, jsonify, g
import firebase_admin
from firebase_admin import auth
from db import db  # <--- Importamos la DB

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'Authorization header is missing'}), 401

        parts = auth_header.split()
        if parts[0].lower() != 'bearer' or len(parts) != 2:
            return jsonify({'error': 'Authorization header must be Bearer token'}), 401

        token = parts[1]

        try:
            decoded_token = auth.verify_id_token(token)
            g.user_id = decoded_token['uid']
            
            # --- NUEVA LÓGICA: Consultar rol en Firestore ---
            # Esto valida contra tu "colección extra"
            g.is_admin = False
            if db:
                user_doc = db.collection('clients').document(g.user_id).get()
                if user_doc.exists:
                    # Asumimos que el campo se llama 'admin' (booleano)
                    g.is_admin = user_doc.to_dict().get('admin', False)
            # -----------------------------------------------

        except Exception as e:
            return jsonify({'error': f'Authentication failed: {str(e)}'}), 401

        return f(*args, **kwargs)
    return decorated_function