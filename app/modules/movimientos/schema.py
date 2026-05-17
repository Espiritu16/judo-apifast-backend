from pydantic import BaseModel, ConfigDict, Field
"""Clases que representan los datos que se transmitirán 
entre servidor y cliente a través de las APIs relacionadas al módulo de movimientos"""
class MovimientoCreate(BaseModel):
    id_producto: int
    tipo_movimiento: str
    cantidad: float = Field(gt=0)
    costo_unitario: float | None = Field(default=None, ge=0)
    motivo: str
    referencia: str | None = None
    observacion: str | None = None
class MovimientoOut(BaseModel):
    id_movimiento: int
    id_producto: int
    tipo_movimiento: str
    cantidad: float
    costo_unitario: float | None
    motivo: str
    referencia: str | None
    observacion: str | None
    model_config = ConfigDict(from_attributes=True)