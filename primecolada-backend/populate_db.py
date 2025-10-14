import random
import os
from faker import Faker
from datetime import datetime, timedelta
from google.cloud import firestore
from db import db  # Import the Firestore client from db.py
from enums import VentaState

# Initialize Faker
fake = Faker('es_ES')

# A reference to the 'ventas' collection
ventas_collection = db.collection('ventas') if db else None
clients_collection = db.collection('clients') if db else None

def create_random_venta():
    """Creates a random venta payload with a simulated lifecycle."""
    nombre = fake.name()
    telefono = int(fake.unique.random_number(digits=9))
    
    # Generate random costs
    coste_lavadora = random.randint(5, 20) if random.choice([True, False]) else None
    coste_secadora = random.randint(5, 15) if random.choice([True, False]) else None
    total = (coste_lavadora or 0) + (coste_secadora or 0)

    # Simulate a credible lifecycle
    now = datetime.now()
    created_at = now - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23), minutes=random.randint(0, 59))
    
    # Define the state progression, excluding ERROR
    possible_states = [s for s in VentaState if s != VentaState.ERROR]
    
    # Randomly decide how far in the lifecycle this venta is
    current_state_index = random.randint(0, len(possible_states) - 1)
    estado_actual = possible_states[current_state_index]

    historial_estados = {}
    current_time = created_at

    for i in range(current_state_index + 1):
        state = possible_states[i]
        entrada = current_time
        
        # Add a random delay for each state transition
        delay = timedelta(minutes=random.randint(5, 120))
        salida = current_time + delay
        
        if i == current_state_index:
            salida = None  # Current state has no exit time

        historial_estados[str(state.value)] = {
            'entrada': entrada,
            'salida': salida
        }
        
        if salida:
            current_time = salida

    # Create the payload
    payload = {
        "nombre": nombre,
        "telefono": telefono,
        "estado_actual": estado_actual.value,
        "coste": {
            "lavadora": coste_lavadora,
            "secadora": coste_secadora,
            "total": total
        },
        "created_at": created_at,
        "updated_at": current_time,
        "historial_estados": historial_estados
    }
    return payload

def populate_db():
    """Populates the database with a given number of ventas."""
    num_ventas = int(os.getenv("NUM_VENTAS", 20))
    if not ventas_collection or not clients_collection:
        print("Firestore not initialized. Aborting population.")
        return

    for i in range(num_ventas):
        venta_data = create_random_venta()
        
        try:
            # Upsert client
            client_id = str(venta_data['telefono'])
            client_ref = clients_collection.document(client_id)
            if not client_ref.get().exists:
                client_ref.set({
                    'nombre': venta_data['nombre'],
                    'telefono': venta_data['telefono'],
                    'created_at': firestore.SERVER_TIMESTAMP
                })

            # Add a new document with an auto-generated ID and default state
            update_time, doc_ref = ventas_collection.add(venta_data)
            print(f"Successfully created venta {i+1}/{num_ventas} with ID: {doc_ref.id}")
        except Exception as e:
            print(f"Error creating venta {i+1}/{num_ventas}: {e}")

if __name__ == "__main__":
    print("Starting database population...")
    populate_db()
    print("Database population finished.")
