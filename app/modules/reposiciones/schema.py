from pydantic import BaseModel, Field
"""Clases que representan los datos que se transmitirán 
entre servidor y cliente a través de las APIs relacionadas al módulo de reposiciones"""
class DetalleReposicionIn(BaseModel):
    id_producto: int
    cantidad_solicitada: float = Field(gt=0)
    costo_unitario: float = Field(ge=0)
class ReposicionCreate(BaseModel):
    codigo_reposicion: str
    id_proveedor: int
    observacion: str | None = None
    detalles: list[DetalleReposicionIn]
class DetalleReposicionUpdateIn(BaseModel):
    id_producto: int
    cantidad_solicitada: float = Field(ge=0)
    costo_unitario: float = Field(ge=0)
class ReposicionUpdate(BaseModel):
    id_proveedor: int
    observacion: str | None = None
    detalles: list[DetalleReposicionUpdateIn]
class ReposicionEstadoUpdate(BaseModel):
    nuevo_estado: str
    observacion: str | None = None
class RecibirDetalleIn(BaseModel):
    id_detalle_reposicion: int
    cantidad_recibida: float = Field(gt=0)
class RecibirReposicionIn(BaseModel):
    detalles: list[RecibirDetalleIn]
    observacion: str | None = None
