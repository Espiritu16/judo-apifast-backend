from pydantic import BaseModel, ConfigDict
"""Clases que representan los datos que se transmitirán 
entre servidor y cliente a través de las APIs relacionadas al módulo de proveedores"""
class ProveedorCreate(BaseModel):
    razon_social: str
    ruc: str | None = None
    telefono: str | None = None
    correo_electronico: str | None = None
class ProveedorUpdate(BaseModel):
    razon_social: str
    ruc: str | None = None
    telefono: str | None = None
    correo_electronico: str | None = None
class InactivarPayload(BaseModel):
    motivo: str
class ProveedorOut(BaseModel):
    id_proveedor: int
    razon_social: str
    ruc: str | None
    telefono: str | None
    correo_electronico: str | None
    estado: str
    model_config = ConfigDict(from_attributes=True)