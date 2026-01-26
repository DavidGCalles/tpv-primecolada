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

    # 1. Search for existing user (Shadow or Registered) by phone
    # We cast to string to ensure consistency with Firestore queries
    query = clients_collection.where('telefono', '==', str(telefono)).limit(1)
    results = list(query.stream())

    if results:
        # Client exists, return their ID
        doc_id = results[0].id
        logging.info(f"Existing client found for phone {telefono}: {doc_id}")
        return doc_id
    else:
        # 2. Create Shadow User
        new_client_data = {
            'nombre': nombre,
            'telefono': str(telefono),
            'firebase_uid': None,  # Explicitly None indicates Shadow User
            'created_at': firestore.SERVER_TIMESTAMP
        }
        update_time, doc_ref = clients_collection.add(new_client_data)
        logging.info(f"Shadow User created: {doc_ref.id} for phone {telefono}")
        return doc_ref.id