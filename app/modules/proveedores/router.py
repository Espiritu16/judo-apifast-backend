from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.deps import get_current_user, get_db, require_roles
from app.modules.proveedores.schema import InactivarPayload, ProveedorCreate, ProveedorUpdate
from app.modules.proveedores.service import ProveedorService  as ProveedorServ
from app.modules.usuarios.model import Usuario
from app.shared.responses import respuesta_ok
router = APIRouter()
#API para agregar 1 proveedor al sistema
@router.post('')
def crear_proveedor(payload: ProveedorCreate, db: Session = Depends(get_db), user: Usuario = Depends(require_roles('DUENA'))):
    return respuesta_ok('Proveedor creado', ProveedorServ.crear_proveedor(db, payload.model_dump(), user.id_usuario))
#API para obtener la lista de proveedores
@router.get('')
def listar_proveedores(db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    return respuesta_ok('Proveedores listados', ProveedorServ.listar_proveedores(db))
#API para obtener 1 proveedor en base a su ID
@router.get('/{id_proveedor}')
def obtener_proveedor(id_proveedor: int, db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    return respuesta_ok('Proveedor encontrado', ProveedorServ.obtener_proveedor(db, id_proveedor))
#API para actualizar 1 proveedor en base a su ID
@router.put('/{id_proveedor}')
def actualizar_proveedor(id_proveedor: int, payload: ProveedorUpdate, db: Session = Depends(get_db), user: Usuario = Depends(require_roles('DUENA'))):
    return respuesta_ok('Proveedor actualizado', ProveedorServ.actualizar_proveedor(db, id_proveedor, payload.model_dump(), user.id_usuario))
#API para desactivar 1 proveedor en base a su ID y hacerlo no
@router.patch('/{id_proveedor}/inactivar')
def inactivar_proveedor(id_proveedor: int, payload: InactivarPayload, db: Session = Depends(get_db), user: Usuario = Depends(require_roles('DUENA'))):
    return respuesta_ok('Proveedor inactivado', ProveedorServ.inactivar_proveedor(db, id_proveedor, payload.motivo, user.id_usuario))

