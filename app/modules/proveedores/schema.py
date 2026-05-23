from pydantic import BaseModel, ConfigDict, Field


class ProveedorCreate(BaseModel):
    razon_social: str = Field(min_length=3, max_length=120)
    ruc: str | None = Field(default=None, min_length=11, max_length=11)
    telefono: str | None = Field(default=None, max_length=20)
    correo_electronico: str | None = Field(default=None, max_length=120)


class ProveedorUpdate(BaseModel):
    razon_social: str = Field(min_length=3, max_length=120)
    ruc: str | None = Field(default=None, min_length=11, max_length=11)
    telefono: str | None = Field(default=None, max_length=20)
    correo_electronico: str | None = Field(default=None, max_length=120)


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
