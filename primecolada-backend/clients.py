from flask import Blueprint, request, jsonify, g
from google.cloud import firestore
from db import db
from flask_jwt_extended import create_access_token, get_jwt
from auth_middleware import token_required
from models import client_schema
import logging
from utils import merge_shadow_user

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
    Authenticate a client AND perform Identity Resolution (Merging).
    """
    if not clients_collection:
        return jsonify({"error": "Firestore not initialized"}), 500
    try:
        uid = g.user_id
        data = request.get_json() or {}
        phone_input = data.get('telefono')
        
        # 1. ¿Existe ya un usuario registrado con este UID?
        query_uid = clients_collection.where('firebase_uid', '==', uid).limit(1)
        results_uid = list(query_uid.stream())
        
        existing_doc = results_uid[0] if results_uid else None
        final_doc_id = existing_doc.id if existing_doc else None
        client_data = existing_doc.to_dict() if existing_doc else {}

        # 2. LOGIC DE MERGE (Si hay teléfono)
        if phone_input:
            claimed_shadow_id = merge_shadow_user(uid, phone_input)
            
            if claimed_shadow_id:
                # ¡Éxito! Hemos reclamado una cuenta antigua.
                final_doc_id = claimed_shadow_id
                
                # LIMPIEZA: Si teníamos una cuenta "vacía" (creada antes) y ahora hemos 
                # reclamado otra (la sombra), la cuenta vacía ya no sirve.
                # (Solo si son IDs diferentes, claro)
                if existing_doc and existing_doc.id != claimed_shadow_id:
                    logging.info(f"CLEANUP: Deleting obsolete empty profile {existing_doc.id}")
                    clients_collection.document(existing_doc.id).delete()
                
                # Refrescamos los datos finales
                client_data = clients_collection.document(final_doc_id).get().to_dict()

        # 3. SI AÚN NO TENEMOS CUENTA (Ni existente, ni fusionada) -> CREAR NUEVA
        if not final_doc_id:
            new_data = {
                'firebase_uid': uid,
                'nombre': data.get('nombre', 'Usuario Digital'),
                'created_at': firestore.SERVER_TIMESTAMP
            }
            if phone_input:
                new_data['telefono'] = str(phone_input)
                
            update_time, doc_ref = clients_collection.add(new_data)
            final_doc_id = doc_ref.id
            client_data = new_data
            logging.info(f"NEW USER: Created profile {final_doc_id} for {uid}")

        # Generate Token (Siempre apunta al final_doc_id resuelto)
        is_admin = client_data.get('admin', False)
        access_token = create_access_token(
            identity=final_doc_id, 
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
