from pydantic import BaseModel, ConfigDict, Field
"""Clases que representan los datos que se transmitirán 
entre servidor y cliente a través de las APIs relacionadas al módulo de productos"""
class ProductoCreate(BaseModel):
    codigo_producto: str
    nombre_producto: str
    descripcion: str | None = None
    id_categoria: int
    unidad_medida: str
    costo_unitario_actual: float = Field(ge=0)
class ProductoUpdate(BaseModel):
    nombre_producto: str
    descripcion: str | None = None
    id_categoria: int
    unidad_medida: str
    costo_unitario_actual: float = Field(ge=0)
class InactivarPayload(BaseModel):
    motivo: str
class ProductoOut(BaseModel):
    id_producto: int
    codigo_producto: str
    nombre_producto: str
    descripcion: str | None
    id_categoria: int
    unidad_medida: str
    costo_unitario_actual: float
    estado: str
    model_config = ConfigDict(from_attributes=True)
