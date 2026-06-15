from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_roles
from app.modules.auditoria.service import AuditoriaService
from app.modules.usuarios.model import Usuario
from app.shared.responses import respuesta_ok


router = APIRouter()


@router.get("")
def listar_eventos_auditoria(
    desde: date | None = None,
    hasta: date | None = None,
    modulo: str | None = None,
    accion: str | None = None,
    resultado: str | None = None,
    idUsuario: int | None = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_roles("DUEÑA")),
):
    return respuesta_ok(
        "Eventos de auditoría listados",
        AuditoriaService(db).listar_eventos(
            desde=desde,
            hasta=hasta,
            modulo=modulo,
            accion=accion,
            resultado=resultado,
            id_usuario=idUsuario,
            limit=limit,
        ),
    )
