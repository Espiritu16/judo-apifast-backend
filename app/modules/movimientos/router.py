from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.deps import get_current_user, get_db, require_roles
from app.modules.movimientos.schema import MovimientoCreate
from app.modules.movimientos.service import MovimientoService as MovimientoServ
from app.modules.usuarios.model import Usuario
from app.shared.responses import respuesta_ok
router = APIRouter()
@router.post('')
def crear_movimiento(payload: MovimientoCreate, db: Session = Depends(get_db), user: Usuario = Depends(require_roles('DUEÑA', 'EMPLEADO'))):
    movimiento = MovimientoServ(db).registrar_movimiento(payload.model_dump(), user)
    return respuesta_ok('Movimiento registrado', {'id_movimiento': movimiento.id_movimiento, 'id_producto': movimiento.id_producto})
@router.get('')
def listar_movimientos(db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    return respuesta_ok('Movimientos listados', MovimientoServ(db).listar_movimientos())
@router.get('/{id_movimiento}')
def obtener_movimiento(id_movimiento: int, db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    return respuesta_ok('Movimiento encontrado', MovimientoServ(db).obtener_movimiento(id_movimiento))
