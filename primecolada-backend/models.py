from marshmallow import Schema, fields, validate, EXCLUDE
from enums import VentaState

class CosteSchema(Schema):
    class Meta:
        unknown = EXCLUDE
    
    lavadora = fields.Int(required=False, allow_none=True)
    secadora = fields.Int(required=False, allow_none=True)
    total = fields.Int(required=True)

class HistorialEntrySchema(Schema):
    class Meta:
        unknown = EXCLUDE
    
    entrada = fields.DateTime(required=True, allow_none=True)
    salida = fields.DateTime(required=False, allow_none=True)

class ClientSchema(Schema):
    class Meta:
        unknown = EXCLUDE
    
    id = fields.Str(dump_only=True)
    nombre = fields.Str(required=True)
    telefono = fields.Str(required=True)
    firebase_uid = fields.Str(required=False, allow_none=True)
    created_at = fields.DateTime(dump_only=True)

class VentaSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id = fields.Str(dump_only=True)
    client_id = fields.Str(dump_only=True) 
    
    telefono = fields.Str(required=True) 
    nombre = fields.Str(required=True)
    
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    estado_actual = fields.Int(
        load_default=VentaState.EN_COLA.value,
        validate=validate.OneOf([e.value for e in VentaState]),
    )

    coste = fields.Nested(CosteSchema, required=True)

    historial_estados = fields.Dict(
        keys=fields.Str(),
        values=fields.Nested(HistorialEntrySchema),
        dump_only=True
    )

class PublicVentaSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id = fields.Str(dump_only=True)
    estado_actual = fields.Int(required=True)
    coste = fields.Nested(CosteSchema, only=("total",), dump_only=True) 
    updated_at = fields.DateTime(dump_only=True)
    
    # Campo calculado para la privacidad
    alias = fields.Method("get_masked_name")

    def get_masked_name(self, obj):
        """
        Transforma 'Pepito Grillo' en 'Pepito G.'
        Si no hay nombre, devuelve 'Cliente'.
        """
        raw_name = obj.get('nombre', '')
        if not raw_name:
            return "Cliente"
        
        parts = raw_name.strip().split()
        if len(parts) > 1:
            # Toma el primer nombre y la inicial del último
            return f"{parts[0]} {parts[-1][0]}."
        else:
            # Si solo hay un nombre, lo devolvemos tal cual (riesgo aceptable)
            return parts[0]

public_venta_schema = PublicVentaSchema()

venta_schema = VentaSchema()
ventas_schema = VentaSchema(many=True)

client_schema = ClientSchema()
clients_schema = ClientSchema(many=True)