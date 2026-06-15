from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AuditoriaEventoOut(BaseModel):
    id_auditoria: int
    id_usuario: int | None
    accion: str
    modulo: str
    entidad: str | None
    id_entidad: int | None
    resultado: str
    codigo_error: str | None
    mensaje: str | None
    metodo: str | None
    ruta: str | None
    ip: str | None
    user_agent: str | None
    metadata: dict[str, Any] | None = Field(default=None)
    fecha_creacion: datetime
    model_config = ConfigDict(from_attributes=True)
