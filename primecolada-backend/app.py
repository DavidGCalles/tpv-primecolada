import os
from flask import Flask, jsonify
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS
import firebase_admin
import logging
from flask_jwt_extended import JWTManager

# Import routes and swagger spec
from routes import api
from clients import clients_api
from swagger_spec import get_swagger_spec
import db  # Import the db module to initialize Firestore

# ... arriba del todo ...
from auth_middleware import token_required 
from flask import g

# Initialize Flask App
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# JWT Configuration
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key')  # Change this to a secure key
jwt = JWTManager(app)

if not firebase_admin._apps:
    firebase_admin.initialize_app()

# --- Swagger UI Configuration ---
SWAGGER_URL = '/api/docs'
API_URL = '/static/swagger.json'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': "Firestore Flask API"}
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
app.register_blueprint(api)
app.register_blueprint(clients_api)

@app.route('/static/swagger.json')
def swagger_spec_json():
    """Serve the swagger.json file."""
    return jsonify(get_swagger_spec())


@app.route('/test-auth', methods=['GET'])
@token_required
def test_auth():
    return jsonify({'message': '¡Estás dentro!', 'uid': g.user_id}), 200

if __name__ == '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
