import requests
import os
from flask import Blueprint, request, jsonify, g
from datetime import datetime
from google.cloud import firestore
from db import db  # Import the Firestore client from db.py
from enums import VentaState
from models import venta_schema, ventas_schema, public_venta_schema
from marshmallow import ValidationError
from auth_middleware import token_required
from functools import wraps
from utils import get_or_create_client_by_phone

# Create a Blueprint for the routes
api = Blueprint('api', __name__)

def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            # CAMBIO: Usamos la variable global g que rellenó el middleware
            if g.get('is_admin'):
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

@api.route('/user/profile', methods=['GET'])
@token_required
def get_user_profile():
    """
    Get the current user's profile information.
    
    Returns:
        JSON: User ID and admin status.
    """
    return jsonify({
        'user_id': g.user_id,
        'is_admin': g.is_admin
    })

@api.route('/ventas', methods=['POST'])
@token_required
def create_venta():
    """
    Create a new venta in Firestore.
    ADR-003: Accepts 'telefono' instead of 'client_id'.
    """
    if not db:
        return jsonify({"error": "Firestore not initialized"}), 500
    try:
        data = request.get_json()
        
        # Validate payload (Ensure models.py VentaSchema requires telefono, not client_id)
        try:
            validated_data = venta_schema.load(data)
        except ValidationError as err:
            return jsonify(err.messages), 400

        # --- SHADOW USER RESOLUTION ---
        # We trust the helper to find the ID or create a ghost user
        try:
            client_doc_id = get_or_create_client_by_phone(
                validated_data['telefono'], 
                validated_data['nombre']
            )
        except Exception as e:
            return jsonify({"error": f"Resolution failed: {str(e)}"}), 500
        # ------------------------------

        # Construct the Venta document
        doc_data = validated_data
        doc_data['client_id'] = client_doc_id  # Link the sale to the resolved ID
        
        now = datetime.now()
        doc_data['created_at'] = now
        doc_data['updated_at'] = now
        doc_data['historial_estados'] = {
            str(validated_data['estado_actual']): {
                'entrada': now,
                'salida': None
            }
        }
        
        # Save to Firestore
        ventas_collection = db.collection('ventas')
        update_time, doc_ref = ventas_collection.add(doc_data)
        
        return jsonify({
            "id": doc_ref.id, 
            "client_id": client_doc_id,
            "message": "Venta created and linked to Client (Shadow or Registered)"
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@api.route('/ventas', methods=['GET'])
@token_required
def get_ventas():
    """
    Get all ventas from Firestore, with optional filtering.

    Retrieves documents from the 'ventas' collection. If a 'client_id'
    query parameter is provided, it filters the ventas for that client.
    Otherwise, it returns all ventas.

    Returns:
        JSON: A list of ventas or an error message.
    """
    if not ventas_collection:
        return jsonify({"error": "Firestore not initialized"}), 500
    try:
        client_id_filter = request.args.get('client_id')
        
        if client_id_filter:
            query = ventas_collection.where('client_id', '==', client_id_filter)
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
@token_required
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

@api.route('/ventas/stats', methods=['GET'])
@token_required
def get_ventas_stats():
    """
    Get sales statistics for the current day.

    Returns:
        JSON: A dictionary with total_precio, total_ventas, and pedidos_antiguos.
    """
    if not ventas_collection:
        return jsonify({"error": "Firestore not initialized"}), 500
    try:
        now = datetime.now()
        start_of_day = datetime(now.year, now.month, now.day)
        
        # Daily stats
        query_today = ventas_collection.where('created_at', '>=', start_of_day)
        total_precio_today = 0
        total_ventas_today = 0
        for doc in query_today.stream():
            venta = doc.to_dict()
            if venta.get('coste'):
                total_precio_today += venta.get('coste').get('total', 0)
            total_ventas_today += 1
            
        # Old pending orders
        query_old = ventas_collection.where('created_at', '<', start_of_day)
        pedidos_antiguos = 0
        for doc in query_old.stream():
            venta = doc.to_dict()
            if venta.get('estado_actual') not in [VentaState.ENTREGADO.value, VentaState.CANCELADO.value]:
                pedidos_antiguos += 1

        return jsonify({
            "total_precio": total_precio_today,
            "total_ventas": total_ventas_today,
            "pedidos_antiguos": pedidos_antiguos
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/ventas/<string:venta_id>', methods=['GET'])
@token_required
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
@token_required
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
            return jsonify({"success": True}), 200
        else:
            return jsonify({"error": "Venta not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/ventas/<string:venta_id>', methods=['DELETE'])
@token_required
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
            return jsonify({"success": True}), 200
        else:
            return jsonify({"error": "Venta not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/public/ventas/<string:venta_id>', methods=['GET'])
def get_public_venta_traceability(venta_id):
    """
    Returns sanitized status of a sale. No Auth required.
    """
    if not ventas_collection:
        return jsonify({"error": "Firestore not initialized"}), 500
    
    try:
        doc_ref = ventas_collection.document(venta_id)
        doc = doc_ref.get()
        
        if doc.exists:
            venta = doc.to_dict()
            venta['id'] = doc.id
            
            # APLICAMOS LA MÁSCARA: Solo salen los datos definidos en PublicVentaSchema
            return jsonify(public_venta_schema.dump(venta)), 200
        else:
            # Devolvemos 404 genérico para no filtrar información
            return jsonify({"error": "Order not found"}), 404

    except Exception as e:
        print(f"Error public endpoint: {str(e)}") 
        return jsonify({"error": "Error retrieving status"}), 500