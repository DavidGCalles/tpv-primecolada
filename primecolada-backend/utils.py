import logging
from google.cloud import firestore
from db import db

def get_or_create_client_by_phone(telefono, nombre):
    """
    Searches for a client by phone.
    - If found: Returns the existing Document ID.
    - If not found: Creates a 'Shadow User' (no firebase_uid) and returns new ID.
    """
    if not db:
        raise Exception("Firestore not initialized")

    clients_collection = db.collection('clients')
    query = clients_collection.where('telefono', '==', str(telefono)).limit(1)
    results = list(query.stream())

    if results:
        doc_id = results[0].id
        logging.info(f"Existing client found for phone {telefono}: {doc_id}")
        return doc_id
    else:
        new_client_data = {
            'nombre': nombre,
            'telefono': str(telefono),
            'firebase_uid': None,
            'created_at': firestore.SERVER_TIMESTAMP
        }
        update_time, doc_ref = clients_collection.add(new_client_data)
        logging.info(f"Shadow User created: {doc_ref.id} for phone {telefono}")
        return doc_ref.id

def merge_shadow_user(firebase_uid, telefono):
    """
    Intenta fusionar un usuario autenticado (firebase_uid) con un perfil sombra existente.
    
    Retorna:
        - (str) ID del documento sombra reclamado (si hubo fusión).
        - None (si no se encontró sombra o no era necesaria fusión).
    """
    if not db or not telefono:
        return None

    clients_collection = db.collection('clients')
    
    # Buscamos si existe un perfil sombra con este teléfono
    # CRÍTICO: Debe ser un perfil que NO tenga firebase_uid asignado (o sea null)
    # Pero Firestore query con '== None' puede ser tricky, mejor buscamos por telefono y filtramos en código
    # para asegurar que no robamos la cuenta a otro usuario registrado.
    
    query = clients_collection.where('telefono', '==', str(telefono)).limit(1)
    results = list(query.stream())
    
    if results:
        shadow_doc = results[0]
        shadow_data = shadow_doc.to_dict()
        current_owner = shadow_data.get('firebase_uid')

        # REGLA ESTRICTA DE SEGURIDAD:
        # 1. Si el perfil encontrado tiene un `firebase_uid`...
        # 2. ...Y ese `firebase_uid` NO es el del usuario que hace la petición...
        # 3. ...Se aborta la operación para evitar robo de identidad.
        if current_owner and current_owner != firebase_uid:
            logging.warning(f"SECURITY ALERT: User {firebase_uid} attempted to claim phone number {telefono} already owned by {current_owner}.")
            return None  # Abortar

        # Si el perfil no tiene dueño (es un "Shadow User"), lo reclamamos.
        if not current_owner:
            clients_collection.document(shadow_doc.id).update({
                'firebase_uid': firebase_uid,
                'updated_at': firestore.SERVER_TIMESTAMP
            })
            logging.info(f"MERGE SUCCESS: User {firebase_uid} claimed Shadow profile {shadow_doc.id}")
            return shadow_doc.id
        
        # Si el `firebase_uid` es el nuestro, la operación es idempotente.
        # Simplemente retornamos el ID correcto.
        return shadow_doc.id
            
    return None