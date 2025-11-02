import requests
import os
from flask import Blueprint, request, jsonify
from datetime import datetime
from google.cloud import firestore
from db import db  # Import the Firestore client from db.py
from enums import VentaState
from models import venta_schema, ventas_schema
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required, get_jwt
from functools import wraps

# Create a Blueprint for the routes
api = Blueprint('api', __name__)

def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            claims = get_jwt()
            if claims.get('is_admin'):
                return fn(*args, **kwargs)
            else:
                return jsonify(msg="Admins only!"), 403
        return decorator
    return wrapper

def convert_timestamps(data):
    """
    Recursively convert Firestore DatetimeWithNanoseconds to ISO 8601 strings.
    """
    if isinstance(data, dict):
        return {key: convert_timestamps(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_timestamps(item) for item in data]
    elif isinstance(data, datetime):
        return data.isoformat()
    else:
        return data

# A reference to the 'ventas' collection
ventas_collection = db.collection('ventas') if db else None
clients_collection = db.collection('clients') if db else None

@api.route('/ventas', methods=['POST'])
@jwt_required()
@admin_required()
def create_venta():
    """
    Create a new venta in Firestore.

    This endpoint expects a JSON payload with 'telefono' and 'nombre' fields.
    It adds a new document to the 'ventas' collection with a default state
    of 'IMPRIMIENDO' and a server-side timestamp. If a client with the given
    'telefono' does not exist, a new client will be created.

    Returns:
        JSON: A confirmation message with the new document's ID or an error message.
    """
    if not ventas_collection:
        return jsonify({"error": "Firestore not initialized"}), 500
    try:
        data = request.get_json()
        try:
            validated_data = venta_schema.load(data)
        except ValidationError as err:
            return jsonify(err.messages), 400

        # Upsert client
        client_id = str(validated_data['telefono'])
        client_ref = clients_collection.document(client_id)
        if not client_ref.get().exists:
            client_ref.set({
                'nombre': validated_data['nombre'],
                'telefono': validated_data['telefono'],
                'created_at': firestore.SERVER_TIMESTAMP
            })

        # Add a new document with an auto-generated ID and default state
        doc_data = validated_data
        now = datetime.now()
        doc_data['created_at'] = now
        doc_data['updated_at'] = now
        doc_data['historial_estados'] = {
            str(validated_data['estado_actual']): {
                'entrada': now,
                'salida': None
            }
        }
        update_time, doc_ref = ventas_collection.add(doc_data)
        broadcast_imprimiendo_update()  # broadcast updated list
        return jsonify({"id": doc_ref.id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@api.route('/ventas', methods=['GET'])
@jwt_required()
def get_ventas():
    """
    Get all ventas from Firestore, with optional filtering.

    Retrieves documents from the 'ventas' collection. If a 'telefono'
    query parameter is provided, it filters the ventas for that client.
    Otherwise, it returns all ventas.

    Returns:
        JSON: A list of ventas or an error message.
    """
    if not ventas_collection:
        return jsonify({"error": "Firestore not initialized"}), 500
    try:
        telefono_filter = request.args.get('telefono')
        
        if telefono_filter:
            query = ventas_collection.where('telefono', '==', int(telefono_filter))
        else:
            query = ventas_collection

        all_ventas = []
        for doc in query.stream():
            venta = doc.to_dict()
            venta['id'] = doc.id
            all_ventas.append(venta)
            
        return jsonify(ventas_schema.dump(all_ventas)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/ventas/count', methods=['GET'])
@jwt_required()
@admin_required()
def count_ventas_by_status():
    """
    Count ventas by their current status.

    Iterates through all ventas and returns a count for each status defined in the
    VentaState enum.

    Returns:
        JSON: A dictionary with status counts or an error message.
    """
    if not ventas_collection:
        return jsonify({"error": "Firestore not initialized"}), 500
    try:
        status_counts = {state.value: 0 for state in VentaState}
        for doc in ventas_collection.stream():
            venta = doc.to_dict()
            if 'estado_actual' in venta and venta['estado_actual'] in status_counts:
                status_counts[venta['estado_actual']] += 1
        return jsonify(status_counts), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/ventas/<string:venta_id>', methods=['GET'])
@jwt_required()
def get_venta(venta_id):
    """
    Get a single venta by its ID.

    Args:
        venta_id (str): The unique identifier for the venta.

    Returns:
        JSON: The requested venta's data or a 404 error if not found.
    """
    if not ventas_collection:
        return jsonify({"error": "Firestore not initialized"}), 500
    try:
        doc_ref = ventas_collection.document(venta_id)
        doc = doc_ref.get()
        if doc.exists:
            venta = doc.to_dict()
            venta['id'] = doc.id
            return jsonify(venta_schema.dump(venta)), 200
        else:
            return jsonify({"error": "Venta not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/ventas/<string:venta_id>', methods=['PUT'])
@jwt_required()
@admin_required()
def update_venta(venta_id):
    """
    Update an existing venta.

    Args:
        venta_id (str): The ID of the venta to update.

    This endpoint expects a JSON payload with the fields to be updated.
    It validates the 'telefono' and 'state' fields if they are present.

    Returns:
        JSON: A success message or an error message.
    """
    if not ventas_collection:
        return jsonify({"error": "Firestore not initialized"}), 500
    try:
        data = request.get_json()
        try:
            validated_data = venta_schema.load(data, partial=True)
        except ValidationError as err:
            return jsonify(err.messages), 400
        
        doc_ref = ventas_collection.document(venta_id)
        doc = doc_ref.get()
        if doc.exists:
            existing_venta = doc.to_dict()
            now = datetime.now()
            validated_data['updated_at'] = now

            if 'estado_actual' in validated_data and validated_data['estado_actual'] != existing_venta.get('estado_actual'):
                historial = existing_venta.get('historial_estados', {})
                
                # Close the previous state
                previous_state = str(existing_venta.get('estado_actual'))
                if previous_state in historial:
                    historial[previous_state]['salida'] = now

                # Open the new state
                new_state = str(validated_data['estado_actual'])
                historial[new_state] = {'entrada': now, 'salida': None}
                
                validated_data['historial_estados'] = historial

            doc_ref.update(validated_data)
            broadcast_imprimiendo_update()  # broadcast updated list
            return jsonify({"success": True}), 200
        else:
            return jsonify({"error": "Venta not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/ventas/<string:venta_id>', methods=['DELETE'])
@jwt_required()
@admin_required()
def delete_venta(venta_id):
    """
    Delete a venta from Firestore.

    Args:
        venta_id (str): The ID of the venta to delete.

    Returns:
        JSON: A success message or an error message.
    """
    if not ventas_collection:
        return jsonify({"error": "Firestore not initialized"}), 500
    try:
        doc_ref = ventas_collection.document(venta_id)
        doc = doc_ref.get()
        if doc.exists:
            doc_ref.delete()
            broadcast_imprimiendo_update()  # broadcast updated list
            return jsonify({"success": True}), 200
        else:
            return jsonify({"error": "Venta not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/ventas/imprimiendo', methods=['GET'])
def get_imprimiendo_ventas():
    """
    Get all ventas from Firestore with the state 'IMPRIMIENDO'.

    Returns:
        JSON: A list of ventas in the 'IMPRIMIENDO' state or an error message.
    """
    if not ventas_collection:
        return jsonify({"error": "Firestore not initialized"}), 500
    try:
        query = ventas_collection.where('estado_actual', '==', VentaState.IMPRIMIENDO.value)
        results = []
        for doc in query.stream():
            venta = doc.to_dict()
            venta['id'] = doc.id
            results.append(venta)
        results = convert_timestamps(results)
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def broadcast_imprimiendo_update():
    """
    Fetch and broadcast 'imprimiendo' ventas via WebSocket service.

    Queries the 'ventas' collection for documents where the state is 'IMPRIMIENDO'
    and sends the results to the WebSocket service to be broadcasted to all 
    connected clients.
    """
    if not ventas_collection:
        return
    try:
        query = ventas_collection.where('estado_actual', '==', VentaState.IMPRIMIENDO.value)
        results = []
        for doc in query.stream():
            venta = doc.to_dict()
            venta['id'] = doc.id
            results.append(venta)
        results = convert_timestamps(results)
        
        # Send request to WebSocket service
        websocket_url = os.environ.get('WEBSOCKET_URL', 'http://websockets:3001')
        try:
            requests.post(f'{websocket_url}/broadcast', json={"message": results})
        except requests.exceptions.RequestException as e:
            print(f"Error sending broadcast request: {e}")

    except Exception as e:
        print(f"Error in broadcast_imprimiendo_update: {e}")
