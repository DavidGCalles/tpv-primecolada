from flask import Blueprint, request, jsonify, g
from google.cloud import firestore
from db import db
from flask_jwt_extended import create_access_token, get_jwt
from auth_middleware import token_required
from models import client_schema
import logging
from utils import get_or_create_client_by_phone

clients_api = Blueprint('clients_api', __name__)

clients_collection = db.collection('clients') if db else None

@clients_api.route('/clients', methods=['POST'])
@token_required
def create_client():
    """
    Create a new client in Firestore.

    Expects a JSON payload with 'nombre' and optionally 'telefono'.
    The client ID is the authenticated user's Firebase UID.
    """
    if not clients_collection:
        return jsonify({"error": "Firestore not initialized"}), 500
    try:
        data = request.get_json()
        if not data or 'nombre' not in data:
            return jsonify({"error": "Missing nombre"}), 400
        
        client_id = g.user_id  # Use Firebase UID as client ID
        
        # Check if client already exists
        doc_ref = clients_collection.document(client_id)
        if doc_ref.get().exists:
            return jsonify({"error": "Client already exists"}), 409

        doc_ref.set({
            'nombre': data['nombre'],
            'telefono': data.get('telefono'),  # Optional
            'created_at': firestore.SERVER_TIMESTAMP
        })
        return jsonify({"id": client_id}), 201
    except Exception as e:
        logging.error(f"Error creating client: {e}")
        return jsonify({"error": str(e)}), 500

@clients_api.route('/clients', methods=['GET'])
def get_clients():
    """
    Get all clients from Firestore.
    """
    if not clients_collection:
        return jsonify({"error": "Firestore not initialized"}), 500
    try:
        # Only admins can get all clients
        #if not get_jwt().get('is_admin', False):
        #    return jsonify({"error": "Admin required"}), 403
        
        all_clients = []
        for doc in clients_collection.stream():
            client = doc.to_dict()
            client['id'] = doc.id
            all_clients.append(client)
        return jsonify(all_clients), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@clients_api.route('/clients/<string:client_id>', methods=['GET'])
def get_client(client_id):
    """
    Get a single client by their ID (Firebase UID).
    """
    if not clients_collection:
        return jsonify({"error": "Firestore not initialized"}), 500
    try:
        # For non-admin, only allow access to own data
        if client_id != g.user_id and not get_jwt().get('is_admin', False):
            return jsonify({"error": "Unauthorized"}), 403
        
        doc_ref = clients_collection.document(client_id)
        doc = doc_ref.get()
        if doc.exists:
            return jsonify(doc.to_dict()), 200
        else:
            return jsonify({"error": "Client not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@clients_api.route('/clients/<string:client_id>', methods=['PUT'])
def update_client(client_id):
    """
    Update a client's information.
    """
    if not clients_collection:
        return jsonify({"error": "Firestore not initialized"}), 500
    try:
        # For non-admin, only allow updating own data
        if client_id != g.user_id and not get_jwt().get('is_admin', False):
            return jsonify({"error": "Unauthorized"}), 403
        
        data = request.get_json()
        doc_ref = clients_collection.document(client_id)
        if doc_ref.get().exists:
            doc_ref.update(data)
            return jsonify({"success": True}), 200
        else:
            return jsonify({"error": "Client not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@clients_api.route('/clients/<string:client_id>', methods=['DELETE'])
def delete_client(client_id):
    """
    Delete a client.
    """
    if not clients_collection:
        return jsonify({"error": "Firestore not initialized"}), 500
    try:
        # Only admins can delete clients
        if not get_jwt().get('is_admin', False):
            return jsonify({"error": "Admin required"}), 403
        
        doc_ref = clients_collection.document(client_id)
        if doc_ref.get().exists:
            doc_ref.delete()
            return jsonify({"success": True}), 200
        else:
            return jsonify({"error": "Client not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@clients_api.route('/clients/login', methods=['POST'])
@token_required
def client_login():
    """
    Authenticate a client AND claim their Shadow History.
    """
    if not clients_collection:
        return jsonify({"error": "Firestore not initialized"}), 500
    try:
        uid = g.user_id
        data = request.get_json() or {}
        phone_input = data.get('telefono')
        # Ideally we prefer the phone from the Firebase Token, but input works for MVP

        # 1. Search for ALREADY REGISTERED User (by UID)
        # Note: 'firebase_uid' is the field we added to the Client Schema
        query_uid = clients_collection.where('firebase_uid', '==', uid).limit(1)
        results_uid = list(query_uid.stream())

        final_doc_id = None
        client_data = None

        if results_uid:
            # Case A: User already exists and is claimed.
            doc = results_uid[0]
            final_doc_id = doc.id
            client_data = doc.to_dict()
        
        elif phone_input:
            # Case B: First time logging in. Let's see if they have a ghost.
            # We use the helper to get the ID (it will create a shadow if none exists)
            final_doc_id = get_or_create_client_by_phone(phone_input, data.get('nombre', 'Usuario Digital'))
            
            # NOW WE MERGE: Stamp the Firebase UID onto that document
            doc_ref = clients_collection.document(final_doc_id)
            doc_ref.update({
                'firebase_uid': uid,
                'updated_at': firestore.SERVER_TIMESTAMP
            })
            
            client_data = doc_ref.get().to_dict()
            logging.info(f"MERGE: User {uid} claimed Shadow Account {final_doc_id}")
            
        else:
            return jsonify({"error": "User not registered and no phone provided."}), 404

        # Generate Backend Session Token
        is_admin = client_data.get('admin', False)
        access_token = create_access_token(
            identity=final_doc_id, # IDENTITY IS NOW THE FIRESTORE DOC ID, NOT THE UID
            additional_claims={'is_admin': is_admin, 'firebase_uid': uid}
        )
        
        return jsonify({
            "access_token": access_token, 
            "user": client_data, 
            "id": final_doc_id
        }), 200

    except Exception as e:
        logging.error(f"Login error: {e}")
        return jsonify({"error": str(e)}), 500
    
@clients_api.route('/clients/<string:client_id>/stats', methods=['GET'])
def get_client_stats(client_id):
    """
    Get sales statistics for a specific client.
    """
    if not db:
        return jsonify({"error": "Firestore not initialized"}), 500
    try:
        # Verify the client_id matches the authenticated user
        if client_id != g.user_id:
            return jsonify({"error": "Unauthorized"}), 403
        
        # Query the ventas collection for sales associated with this client_id
        ventas_query = db.collection('ventas').where('client_id', '==', client_id)
        
        total_ventas = 0
        last_purchase_date = None
        
        for venta in ventas_query.stream():
            total_ventas += 1
            venta_data = venta.to_dict()
            if 'created_at' in venta_data:
                if last_purchase_date is None or venta_data['created_at'] > last_purchase_date:
                    last_purchase_date = venta_data['created_at']

        return jsonify({
            "client_id": client_id,
            "total_ventas": total_ventas,
            "last_purchase_date": last_purchase_date
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
