from pydantic import BaseModel, ConfigDict, Field


class ProductoCreate(BaseModel):
    codigo_producto: str = Field(min_length=1, max_length=30)
    nombre_producto: str = Field(min_length=3, max_length=120)
    descripcion: str | None = Field(default=None, max_length=255)
    id_categoria: int
    unidad_medida: str = Field(min_length=1, max_length=20)
    costo_unitario_actual: float = Field(ge=0)


class ProductoUpdate(BaseModel):
    nombre_producto: str = Field(min_length=3, max_length=120)
    descripcion: str | None = Field(default=None, max_length=255)
    id_categoria: int
    unidad_medida: str = Field(min_length=1, max_length=20)
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
