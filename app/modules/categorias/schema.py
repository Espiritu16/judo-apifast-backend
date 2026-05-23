from pydantic import BaseModel, ConfigDict, Field


class CategoriaCreate(BaseModel):
    nombre_categoria: str = Field(min_length=3, max_length=80)
    descripcion: str | None = Field(default=None, max_length=255)


class CategoriaUpdate(BaseModel):
    nombre_categoria: str = Field(min_length=3, max_length=80)
    descripcion: str | None = Field(default=None, max_length=255)


class InactivarPayload(BaseModel):
    motivo: str


class CategoriaOut(BaseModel):
    id_categoria: int
    nombre_categoria: str
    descripcion: str | None
    estado: str
    model_config = ConfigDict(from_attributes=True)
