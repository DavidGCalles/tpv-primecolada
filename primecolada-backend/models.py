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

venta_schema = VentaSchema()
ventas_schema = VentaSchema(many=True)

client_schema = ClientSchema()
clients_schema = ClientSchema(many=True)