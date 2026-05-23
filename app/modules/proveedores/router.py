from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.deps import get_current_user, get_db, require_roles
from app.modules.proveedores.schema import InactivarPayload, ProveedorCategoriasUpdate, ProveedorCreate, ProveedorUpdate
from app.modules.proveedores.service import ProveedorService  as ProveedorServ
from app.modules.usuarios.model import Usuario
from app.shared.responses import respuesta_ok
router = APIRouter()
#API para agregar 1 proveedor al sistema
@router.post('')
def crear_proveedor(payload: ProveedorCreate, db: Session = Depends(get_db), user: Usuario = Depends(require_roles('DUEÑA'))):
    return respuesta_ok('Proveedor creado', ProveedorServ(db).crear_proveedor(payload.model_dump(), user.id_usuario))
#API para obtener la lista de proveedores
@router.get('')
def listar_proveedores(db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    return respuesta_ok('Proveedores listados', ProveedorServ(db).listar_proveedores())
@router.get('/consulta-documento/{documento}')
def consultar_documento_proveedor(documento: str, db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    return respuesta_ok(
        'Consulta de documento exitosa',
        ProveedorServ(db).consultar_documento_para_proveedor(documento),
    )
#API para obtener 1 proveedor en base a su ID
@router.get('/{id_proveedor}')
def obtener_proveedor(id_proveedor: int, db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    return respuesta_ok('Proveedor encontrado', ProveedorServ(db).obtener_proveedor(id_proveedor))
#API para actualizar 1 proveedor en base a su ID
@router.put('/{id_proveedor}')
def actualizar_proveedor(id_proveedor: int, payload: ProveedorUpdate, db: Session = Depends(get_db), user: Usuario = Depends(require_roles('DUEÑA'))):
    return respuesta_ok('Proveedor actualizado', ProveedorServ(db).actualizar_proveedor(id_proveedor, payload.model_dump(), user.id_usuario))
#API para desactivar 1 proveedor en base a su ID y hacerlo no
@router.patch('/{id_proveedor}/inactivar')
def inactivar_proveedor(id_proveedor: int, payload: InactivarPayload, db: Session = Depends(get_db), user: Usuario = Depends(require_roles('DUEÑA'))):
    return respuesta_ok('Proveedor inactivado', ProveedorServ(db).inactivar_proveedor(id_proveedor, payload.motivo, user.id_usuario))


@router.get('/{id_proveedor}/categorias')
def obtener_categorias_proveedor(id_proveedor: int, db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    return respuesta_ok('Categorías del proveedor', ProveedorServ(db).listar_categorias(id_proveedor))


@router.put('/{id_proveedor}/categorias')
def actualizar_categorias_proveedor(
    id_proveedor: int,
    payload: ProveedorCategoriasUpdate,
    db: Session = Depends(get_db),
    user: Usuario = Depends(require_roles('DUEÑA')),
):
    return respuesta_ok(
        'Categorías del proveedor actualizadas',
        ProveedorServ(db).actualizar_categorias(id_proveedor, payload.categoria_ids, user.id_usuario),
    )
