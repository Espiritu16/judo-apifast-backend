from pydantic import BaseModel, Field


class UsuarioCreate(BaseModel):
    nombres: str = Field(min_length=1, max_length=80)
    apellidos: str | None = Field(default=None, max_length=80)
    correo: str = Field(min_length=5, max_length=120)
    rol: str = Field(min_length=3, max_length=30)
    password: str = Field(min_length=8, max_length=128)
    estado: str | None = Field(default='ACTIVO', max_length=10)


class UsuarioUpdate(BaseModel):
    nombres: str = Field(min_length=1, max_length=80)
    apellidos: str | None = Field(default=None, max_length=80)
    correo: str = Field(min_length=5, max_length=120)
    rol: str = Field(min_length=3, max_length=30)
    estado: str = Field(min_length=7, max_length=10)


class UsuarioEstadoUpdate(BaseModel):
    estado: str = Field(min_length=7, max_length=10)
    motivo: str | None = Field(default=None, max_length=255)
