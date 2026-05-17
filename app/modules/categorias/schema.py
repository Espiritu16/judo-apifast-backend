from pydantic import BaseModel, ConfigDict
"""Clases que representan los datos que se transmitirán 
entre servidor y cliente a través de las APIs relacionadas al módulo de categorías"""
class CategoriaCreate(BaseModel):
    nombre_categoria: str
    descripcion: str | None = None
class CategoriaUpdate(BaseModel):
    nombre_categoria: str
    descripcion: str | None = None
class InactivarPayload(BaseModel):
    motivo: str
class CategoriaOut(BaseModel):
    id_categoria: int
    nombre_categoria: str
    descripcion: str | None
    estado: str
    model_config = ConfigDict(from_attributes=True)