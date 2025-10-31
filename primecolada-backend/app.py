import os
from flask import Flask, jsonify
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS
from flask_jwt_extended import JWTManager

# Import routes and swagger spec
from routes import api
from clients import clients_api
from swagger_spec import get_swagger_spec
import db  # Import the db module to initialize Firestore

# Initialize Flask App
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this in your production environment!
jwt = JWTManager(app)

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

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
