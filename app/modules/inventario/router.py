from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.deps import get_current_user, get_db, require_roles
from app.modules.inventario.schema import ParametroInventarioUpdate
from app.modules.inventario.service import InventarioService as InventarioServ
from app.modules.usuarios.model import Usuario
from app.shared.responses import respuesta_ok
router = APIRouter()
"API relacionada a mostrar el stock de los productos en inventario"
@router.get('/stock')
def consultar_stock(q: str | None = None, db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    return respuesta_ok('Stock consultado', InventarioServ(db).consultar_stock(q))

"API relacionada a mostrar el stock de los productos con bajo stock en inventario"
@router.get('/stock/critico')
def stock_critico(db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    return respuesta_ok('Stock critico consultado', InventarioServ(db).stock_critico())

"API relacionada a actualizar los parámetros de 1 producto en específico"
@router.put('/parametros/{id_producto}')
def actualizar_parametros(id_producto: int, payload: ParametroInventarioUpdate, db: Session = Depends(get_db), user: Usuario = Depends(require_roles('DUEÑA'))):
    return respuesta_ok('Parametros de inventario actualizados', InventarioServ(db).actualizar_parametros(id_producto, payload.model_dump(), user.id_usuario))
