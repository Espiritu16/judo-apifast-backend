from datetime import date, datetime, time
from typing import Any

from sqlalchemy.orm import Session

from app.modules.auditoria.model import AuditoriaEvento
from app.modules.auditoria.repository import AuditoriaRepository
from app.shared.dates import LIMA_TZ
from app.shared.exceptions import DominioError


RESULTADOS_VALIDOS = {"EXITO", "ERROR", "DENEGADO"}
MAX_LIMIT = 500


class AuditoriaService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = AuditoriaRepository(db)

    def registrar_evento(
        self,
        accion: str,
        modulo: str,
        resultado: str,
        id_usuario: int | None = None,
        entidad: str | None = None,
        id_entidad: int | None = None,
        codigo_error: str | None = None,
        mensaje: str | None = None,
        metodo: str | None = None,
        ruta: str | None = None,
        ip: str | None = None,
        user_agent: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AuditoriaEvento:
        payload = {
            "id_usuario": id_usuario,
            "accion": self._clean_required(accion, "accion", 80).upper(),
            "modulo": self._clean_required(modulo, "modulo", 50).lower(),
            "entidad": self._clean_optional(entidad, 80),
            "id_entidad": id_entidad,
            "resultado": self._normalize_resultado(resultado),
            "codigo_error": self._clean_optional(codigo_error, 80),
            "mensaje": self._clean_optional(mensaje, 255),
            "metodo": self._clean_optional(metodo, 10),
            "ruta": self._clean_optional(ruta, 255),
            "ip": self._clean_optional(ip, 45),
            "user_agent": self._clean_optional(user_agent, 255),
            "extra_metadata": self._sanitize_metadata(metadata),
        }
        item = self.repo.create(payload)
        self.db.commit()
        self.db.refresh(item)
        return item

    def listar_eventos(
        self,
        desde: date | None = None,
        hasta: date | None = None,
        modulo: str | None = None,
        accion: str | None = None,
        resultado: str | None = None,
        id_usuario: int | None = None,
        limit: int = 100,
    ) -> list[dict]:
        if desde and hasta and desde > hasta:
            raise DominioError("VALIDATION_ERROR", "La fecha inicial no puede ser mayor que la fecha final.", 400)
        if id_usuario is not None and id_usuario <= 0:
            raise DominioError("VALIDATION_ERROR", "id_usuario debe ser mayor que 0.", 400)
        if limit <= 0:
            raise DominioError("VALIDATION_ERROR", "limit debe ser mayor que 0.", 400)

        desde_dt, hasta_dt = self._rango_lima(desde, hasta)
        rows = self.repo.list_all(
            desde=desde_dt,
            hasta=hasta_dt,
            modulo=self._clean_optional(modulo, 50).lower() if modulo else None,
            accion=self._clean_optional(accion, 80).upper() if accion else None,
            resultado=self._normalize_resultado(resultado) if resultado else None,
            id_usuario=id_usuario,
            limit=min(limit, MAX_LIMIT),
        )
        return [self._to_dict(item) for item in rows]

    def _normalize_resultado(self, resultado: str) -> str:
        value = self._clean_required(resultado, "resultado", 20).upper()
        if value not in RESULTADOS_VALIDOS:
            raise DominioError("VALIDATION_ERROR", "resultado debe ser EXITO, ERROR o DENEGADO.", 400)
        return value

    def _clean_required(self, value: str | None, field: str, max_len: int) -> str:
        clean = (value or "").strip()
        if not clean:
            raise DominioError("VALIDATION_ERROR", f"El campo {field} es obligatorio.", 400)
        return clean[:max_len]

    def _clean_optional(self, value: str | None, max_len: int) -> str | None:
        clean = (value or "").strip()
        return clean[:max_len] if clean else None

    def _sanitize_metadata(self, metadata: dict[str, Any] | None) -> dict[str, Any] | None:
        if not metadata:
            return None
        blocked = {"password", "clave", "clave_hash", "token", "access_token", "authorization", "api_key"}
        sanitized = {}
        for key, value in metadata.items():
            normalized_key = str(key).lower()
            if normalized_key in blocked or "password" in normalized_key or "token" in normalized_key:
                sanitized[str(key)] = "[REDACTED]"
            elif isinstance(value, (str, int, float, bool)) or value is None:
                sanitized[str(key)] = value
            else:
                sanitized[str(key)] = str(value)
        return sanitized

    def _rango_lima(self, desde: date | None, hasta: date | None) -> tuple[datetime | None, datetime | None]:
        desde_dt = datetime.combine(desde, time.min).replace(tzinfo=LIMA_TZ).replace(tzinfo=None) if desde else None
        hasta_dt = datetime.combine(hasta, time.max).replace(tzinfo=LIMA_TZ).replace(tzinfo=None) if hasta else None
        return desde_dt, hasta_dt

    def _to_dict(self, item: AuditoriaEvento) -> dict:
        return {
            "id_auditoria": item.id_auditoria,
            "id_usuario": item.id_usuario,
            "accion": item.accion,
            "modulo": item.modulo,
            "entidad": item.entidad,
            "id_entidad": item.id_entidad,
            "resultado": item.resultado,
            "codigo_error": item.codigo_error,
            "mensaje": item.mensaje,
            "metodo": item.metodo,
            "ruta": item.ruta,
            "ip": item.ip,
            "user_agent": item.user_agent,
            "metadata": item.extra_metadata,
            "fecha_creacion": item.fecha_creacion,
        }
