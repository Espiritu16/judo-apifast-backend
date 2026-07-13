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
def crear_producto(payload: ProductoCreate, db: Session = Depends(get_db), user: Usuario = Depends(require_roles('DUEÑA', 'EMPLEADO'))):
    return respuesta_ok('Producto creado', ProductServ(db).crear_producto(payload.model_dump(), user.id_usuario))
"API que muestra todos los productos"
@router.get('')
def listar_productos(db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    return respuesta_ok('Productos listados', ProductServ(db).listar_productos())
"API que muestra 1 producto por su ID"
@router.get('/{id_producto}')
def obtener_producto(id_producto: int, db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    return respuesta_ok('Producto encontrado', ProductServ(db).obtener_producto(id_producto))
"API que actualiza 1 producto por su ID"
@router.put('/{id_producto}')
def actualizar_producto(id_producto: int, payload: ProductoUpdate, db: Session = Depends(get_db), user: Usuario = Depends(require_roles('DUEÑA', 'EMPLEADO'))):
    return respuesta_ok('Producto actualizado', ProductServ(db).actualizar_producto(id_producto, payload.model_dump(), user.id_usuario))
"API que desactiva  1 producto ingresando su ID haciendo que este no este disponible"
@router.patch('/{id_producto}/inactivar')
def inactivar_producto(id_producto: int, payload: InactivarPayload, db: Session = Depends(get_db), user: Usuario = Depends(require_roles('DUEÑA', 'EMPLEADO'))):
    return respuesta_ok('Producto inactivado', ProductServ(db).inactivar_producto(id_producto, payload.motivo, user.id_usuario))
"API que activa 1 producto inactivo por su ID"
@router.patch('/{id_producto}/activar')
def activar_producto(id_producto: int, db: Session = Depends(get_db), user: Usuario = Depends(require_roles('DUEÑA', 'EMPLEADO'))):
    return respuesta_ok('Producto activado', ProductServ(db).activar_producto(id_producto, user.id_usuario))
