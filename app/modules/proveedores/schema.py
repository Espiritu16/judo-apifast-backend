from pydantic import BaseModel, ConfigDict, Field


class ProveedorCreate(BaseModel):
    razon_social: str = Field(min_length=3, max_length=120)
    tipo_documento: str = Field(min_length=3, max_length=3)
    numero_documento: str = Field(min_length=8, max_length=11)
    nombre_completo_persona: str | None = Field(default=None, max_length=180)
    telefono: str | None = Field(default=None, max_length=20)
    correo_electronico: str | None = Field(default=None, max_length=120)
    direccion: str | None = Field(default=None, max_length=255)
    departamento: str | None = Field(default=None, max_length=80)
    provincia: str | None = Field(default=None, max_length=80)
    distrito: str | None = Field(default=None, max_length=80)
    estado_contribuyente: str | None = Field(default=None, max_length=50)
    condicion_contribuyente: str | None = Field(default=None, max_length=50)


class ProveedorUpdate(BaseModel):
    razon_social: str = Field(min_length=3, max_length=120)
    tipo_documento: str = Field(min_length=3, max_length=3)
    numero_documento: str = Field(min_length=8, max_length=11)
    nombre_completo_persona: str | None = Field(default=None, max_length=180)
    telefono: str | None = Field(default=None, max_length=20)
    correo_electronico: str | None = Field(default=None, max_length=120)
    direccion: str | None = Field(default=None, max_length=255)
    departamento: str | None = Field(default=None, max_length=80)
    provincia: str | None = Field(default=None, max_length=80)
    distrito: str | None = Field(default=None, max_length=80)
    estado_contribuyente: str | None = Field(default=None, max_length=50)
    condicion_contribuyente: str | None = Field(default=None, max_length=50)


class InactivarPayload(BaseModel):
    motivo: str


class ProveedorOut(BaseModel):
    id_proveedor: int
    razon_social: str
    tipo_documento: str
    numero_documento: str
    nombre_completo_persona: str | None
    telefono: str | None
    correo_electronico: str | None
    direccion: str | None
    departamento: str | None
    provincia: str | None
    distrito: str | None
    estado_contribuyente: str | None
    condicion_contribuyente: str | None
    estado: str
    model_config = ConfigDict(from_attributes=True)


class FactilizaDniData(BaseModel):
    numero: str | None = None
    nombres: str | None = None
    apellido_paterno: str | None = None
    apellido_materno: str | None = None
    nombre_completo: str | None = None
    departamento: str | None = None
    provincia: str | None = None
    distrito: str | None = None
    direccion: str | None = None
    direccion_completa: str | None = None


class FactilizaDniResponseDto(BaseModel):
    status: int | None = None
    success: bool | None = None
    message: str | None = None
    data: FactilizaDniData | None = None


class FactilizaRucData(BaseModel):
    numero: str | None = None
    nombre_o_razon_social: str | None = None
    tipo_contribuyente: str | None = None
    estado: str | None = None
    condicion: str | None = None
    departamento: str | None = None
    provincia: str | None = None
    distrito: str | None = None
    direccion: str | None = None
    direccion_completa: str | None = None


class FactilizaRucResponseDto(BaseModel):
    status: int | None = None
    success: bool | None = None
    message: str | None = None
    data: FactilizaRucData | None = None


class ConsultaDocumentoResponseDto(BaseModel):
    tipo_documento: str
    numero_documento: str
    nombre_o_razon_social: str
    nombres: str | None = None
    apellido_paterno: str | None = None
    apellido_materno: str | None = None
    direccion: str | None = None
    direccion_completa: str | None = None
    departamento: str | None = None
    provincia: str | None = None
    distrito: str | None = None
    estado_contribuyente: str | None = None
    condicion_contribuyente: str | None = None
