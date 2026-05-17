from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.deps import get_current_user, get_db, require_roles
from app.modules.productos.schema import InactivarPayload, ProductoCreate, ProductoUpdate
from app.modules.productos.service import ProductoService as  ProductServ
from app.modules.usuarios.model import Usuario
from app.shared.responses import respuesta_ok
router = APIRouter()
"API que permite crear un producto"
@router.post('')
def crear_producto(payload: ProductoCreate, db: Session = Depends(get_db), user: Usuario = Depends(require_roles('DUENA'))):
    return respuesta_ok('Producto creado', ProductServ.crear_producto(db, payload.model_dump(), user.id_usuario))
"API que muestra todos los productos"
@router.get('')
def listar_productos(db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    return respuesta_ok('Productos listados', ProductServ.listar_productos(db))
"API que muestra 1 producto por su ID"
@router.get('/{id_producto}')
def obtener_producto(id_producto: int, db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    return respuesta_ok('Producto encontrado', ProductServ.obtener_producto(db, id_producto))
"API que actualiza 1 producto por su ID"
@router.put('/{id_producto}')
def actualizar_producto(id_producto: int, payload: ProductoUpdate, db: Session = Depends(get_db), user: Usuario = Depends(require_roles('DUENA'))):
    return respuesta_ok('Producto actualizado', ProductServ.actualizar_producto(db, id_producto, payload.model_dump(), user.id_usuario))
"API que desactiva  1 producto ingresando su ID haciendo que este no este disponible"
@router.patch('/{id_producto}/inactivar')
def inactivar_producto(id_producto: int, payload: InactivarPayload, db: Session = Depends(get_db), user: Usuario = Depends(require_roles('DUENA'))):
    return respuesta_ok('Producto inactivado', ProductServ.inactivar_producto(db, id_producto, payload.motivo, user.id_usuario))
