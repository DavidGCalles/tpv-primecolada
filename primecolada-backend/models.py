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

class VentaSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id = fields.Str(dump_only=True)
    telefono = fields.Int(required=True)
    nombre = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    estado_actual = fields.Int(
        required=True,
        validate=validate.OneOf([e.value for e in VentaState])
    )

    coste = fields.Nested(CosteSchema, required=True)

    historial_estados = fields.Dict(
        keys=fields.Str(),
        values=fields.Nested(HistorialEntrySchema),
        dump_only=True
    )

venta_schema = VentaSchema()
ventas_schema = VentaSchema(many=True)
