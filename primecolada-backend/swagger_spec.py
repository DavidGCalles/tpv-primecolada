def get_swagger_spec():
    """Returns the Swagger 2.0 specification as a dictionary."""
    return {
        "swagger": "2.0",
        "info": {
            "title": "Firestore Flask API",
            "description": "API to interact with a Firestore database using Flask.",
            "version": "1.0.0"
        },
        "definitions": {
            "Coste": {
                "type": "object",
                "properties": {
                    "lavadora": { "type": "integer" },
                    "secadora": { "type": "integer" },
                    "total": { "type": "integer" }
                }
            },
            "HistorialEntry": {
                "type": "object",
                "properties": {
                    "entrada": { "type": "string", "format": "date-time" },
                    "salida": { "type": "string", "format": "date-time" }
                }
            },
            "Client": {
                "type": "object",
                "properties": {
                    "id": { "type": "string" },
                    "nombre": { "type": "string" },
                    "telefono": { "type": "string" },
                    "created_at": { "type": "string", "format": "date-time" }
                }
            },
            "Venta": {
                "type": "object",
                "properties": {
                    "id": { "type": "string" },
                    "client_id": { "type": "string" },
                    "nombre": { "type": "string" },
                    "created_at": { "type": "string", "format": "date-time" },
                    "updated_at": { "type": "string", "format": "date-time" },
                    "estado_actual": { "type": "integer" },
                    "coste": { "$ref": "#/definitions/Coste" },
                    "historial_estados": {
                        "type": "object",
                        "additionalProperties": { "$ref": "#/definitions/HistorialEntry" }
                    }
                }
            }
        },
        "paths": {
            "/ventas": {
                "get": {
                    "summary": "Get all ventas",
                    "responses": { 
                        "200": { 
                            "description": "A list of ventas",
                            "schema": {
                                "type": "array",
                                "items": { "$ref": "#/definitions/Venta" }
                            }
                        } 
                    }
                },
                "post": {
                    "summary": "Create a new venta",
                    "parameters": [{
                        "in": "body",
                        "name": "body",
                        "required": True,
                        "schema": { "$ref": "#/definitions/Venta" }
                    }],
                    "responses": { "201": { "description": "Venta created successfully" } }
                }
            },
            "/ventas/search": {
                "get": {
                    "summary": "Search for ventas",
                    "parameters": [
                        {
                            "name": "nombre",
                            "in": "query",
                            "type": "string",
                            "required": False,
                            "description": "Filter by nombre"
                        },
                        {
                            "name": "client_id",
                            "in": "query",
                            "type": "string",
                            "required": False,
                            "description": "Filter by client_id"
                        }
                    ],
                    "responses": { "200": { "description": "A list of matching ventas" } }
                }
            },
            "/ventas/count": {
                "get": {
                    "summary": "Count ventas by status",
                    "responses": {
                        "200": {
                            "description": "A JSON object with the count of ventas for each status.",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "0": { "type": "integer", "description": "Count of ventas with status ERROR" },
                                    "1": { "type": "integer", "description": "Count of ventas with status EN_COLA" },
                                    "2": { "type": "integer", "description": "Count of ventas with status LAVANDO" },
                                    "3": { "type": "integer", "description": "Count of ventas with status PTE_RECOGIDA" },
                                    "4": { "type": "integer", "description": "Count of ventas with status RECOGIDO" }
                                }
                            }
                        }
                    }
                }
            },
            "/ventas/stats": {
                "get": {
                    "summary": "Get sales statistics for the current day",
                    "responses": {
                        "200": {
                            "description": "A JSON object with daily sales statistics.",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "total_precio": { "type": "number" },
                                    "total_ventas": { "type": "integer" },
                                    "pedidos_antiguos": { "type": "integer" }
                                }
                            }
                        }
                    }
                }
            },
            "/ventas/{venta_id}": {
                "get": {
                    "summary": "Get a single venta by ID",
                    "parameters": [{ "name": "venta_id", "in": "path", "required": True, "type": "string" }],
                    "responses": { 
                        "200": { 
                            "description": "The venta",
                            "schema": { "$ref": "#/definitions/Venta" }
                        }, 
                        "404": { "description": "Venta not found" } 
                    }
                },
                "put": {
                    "summary": "Update a venta",
                    "parameters": [
                        { "name": "venta_id", "in": "path", "required": True, "type": "string" },
                        {
                            "in": "body",
                            "name": "body",
                            "required": True,
                            "schema": { "$ref": "#/definitions/Venta" }
                        }
                    ],
                    "responses": { "200": { "description": "Venta updated successfully" }, "404": { "description": "Venta not found" } }
                },
                "delete": {
                    "summary": "Delete a venta",
                    "parameters": [{ "name": "venta_id", "in": "path", "required": True, "type": "string" }],
                    "responses": { "200": { "description": "Venta deleted successfully" }, "404": { "description": "Venta not found" } }
                }
            },
            "/clients": {
                "get": {
                    "summary": "Get all clients",
                    "responses": { "200": { "description": "A list of clients" } }
                },
                "post": {
                    "summary": "Create a new client",
                    "parameters": [{
                        "in": "body",
                        "name": "body",
                        "required": True,
                        "schema": { "$ref": "#/definitions/Client" }
                    }],
                    "responses": { "201": { "description": "Client created successfully" } }
                }
            },
            "/clients/{client_id}": {
                "get": {
                    "summary": "Get a single client by ID",
                    "parameters": [{ "name": "client_id", "in": "path", "required": True, "type": "string" }],
                    "responses": { "200": { "description": "The client" }, "404": { "description": "Client not found" } }
                },
                "put": {
                    "summary": "Update a client",
                    "parameters": [
                        { "name": "client_id", "in": "path", "required": True, "type": "string" },
                        {
                            "in": "body",
                            "name": "body",
                            "required": True,
                            "schema": { "$ref": "#/definitions/Client" }
                        }
                    ],
                    "responses": { "200": { "description": "Client updated successfully" }, "404": { "description": "Client not found" } }
                },
                "delete": {
                    "summary": "Delete a client",
                    "parameters": [{ "name": "client_id", "in": "path", "required": True, "type": "string" }],
                    "responses": { "200": { "description": "Client deleted successfully" }, "404": { "description": "Client not found" } }
                }
            },
            "/clients/{client_id}/stats": {
                "get": {
                    "summary": "Get sales statistics for a client",
                    "parameters": [{ "name": "client_id", "in": "path", "required": True, "type": "string" }],
                    "responses": { "200": { "description": "Client statistics" }, "404": { "description": "Client not found" } }
                }
            }
        }
    }
