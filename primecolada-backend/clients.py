from flask import Blueprint, request, jsonify
from google.cloud import firestore
from db import db
from flask_jwt_extended import create_access_token

clients_api = Blueprint('clients_api', __name__)

clients_collection = db.collection('clients') if db else None

@clients_api.route('/clients', methods=['POST'])
def create_client():
    """
    Create a new client in Firestore.

    Expects a JSON payload with 'nombre' and 'telefono'.
    'telefono' is used as the document ID to prevent duplicates.
    """
    if not clients_collection:
        return jsonify({"error": "Firestore not initialized"}), 500
    try:
        data = request.get_json()
        if not data or 'telefono' not in data or 'nombre' not in data:
            return jsonify({"error": "Missing telefono or nombre"}), 400
        
        client_id = str(data['telefono'])
        
        # Check if client already exists
        doc_ref = clients_collection.document(client_id)
        if doc_ref.get().exists:
            return jsonify({"error": "Client with this telefono already exists"}), 409

        doc_ref.set({
            'nombre': data['nombre'],
            'telefono': data['telefono'],
            'created_at': firestore.SERVER_TIMESTAMP
        })
        return jsonify({"id": client_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@clients_api.route('/clients', methods=['GET'])
def get_clients():
    """
    Get all clients from Firestore.
    """
    if not clients_collection:
        return jsonify({"error": "Firestore not initialized"}), 500
    try:
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
    Get a single client by their ID (telefono).
    """
    if not clients_collection:
        return jsonify({"error": "Firestore not initialized"}), 500
    try:
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
        doc_ref = clients_collection.document(client_id)
        if doc_ref.get().exists:
            doc_ref.delete()
            return jsonify({"success": True}), 200
        else:
            return jsonify({"error": "Client not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@clients_api.route('/clients/login', methods=['POST'])
def client_login():
    """
    Authenticate a client by their phone number.
    """
    if not clients_collection:
        return jsonify({"error": "Firestore not initialized"}), 500
    try:
        data = request.get_json()
        if not data or 'telefono' not in data:
            return jsonify({"error": "Missing telefono"}), 400
        
        client_id = str(data['telefono'])
        doc_ref = clients_collection.document(client_id)
        doc = doc_ref.get()
        
        if doc.exists:
            client_data = doc.to_dict()
            is_admin = client_data.get('admin', False)
            access_token = create_access_token(identity=client_id, additional_claims={'is_admin': is_admin})
            return jsonify(access_token=access_token, user=client_data), 200
        else:
            return jsonify({"error": "Client not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@clients_api.route('/clients/<string:client_id>/stats', methods=['GET'])
def get_client_stats(client_id):
    """
    Get sales statistics for a specific client.
    """
    if not db:
        return jsonify({"error": "Firestore not initialized"}), 500
    try:
        # First, check if the client exists
        client_doc = clients_collection.document(client_id).get()
        if not client_doc.exists:
            return jsonify({"error": "Client not found"}), 404
        
        client_telefono = client_doc.to_dict().get('telefono')

        # Query the ventas collection for sales associated with this client's telefono
        ventas_query = db.collection('ventas').where('telefono', '==', client_telefono)
        
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
