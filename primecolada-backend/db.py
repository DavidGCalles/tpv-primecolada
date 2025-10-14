from google.cloud import firestore
import os
from dotenv import load_dotenv

load_dotenv()

# Set the environment variable for Google Cloud credentials
# This tells the library where to find your service account key file.
google_credentials = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
if google_credentials:
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = google_credentials

# Initialize the Firestore client.
# The client will automatically use the credentials from the environment variable.
try:
    db = firestore.Client(database=os.getenv('FIRESTORE_DATABASE', 'primecolada-ventas'))
    print(f"Successfully connected to Firestore database '{os.getenv('FIRESTORE_DATABASE')}' using google-cloud-firestore.")
except Exception as e:
    print(f"Could not initialize Firestore. Please check your service account key path and project configuration. Error: {e}")
    db = None
