from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db, require_roles
from app.modules.categorias.schema import CategoriaCreate, CategoriaUpdate, InactivarPayload
from app.modules.categorias.service import CategoriaService as CategoriaServ
from app.modules.usuarios.model import Usuario
from app.shared.responses import respuesta_ok

router = APIRouter()

"API para crear una categoría"
@router.post('')
def crear_categoria(payload: CategoriaCreate, db: Session = Depends(get_db), user: Usuario = Depends(require_roles('DUENA'))):
    return respuesta_ok('Categoria creada', CategoriaServ.crear_categoria(db, payload.model_dump(), user.id_usuario))

"API para mostrar las categorías existentes"
@router.get('')
def listar_categorias(db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    return respuesta_ok('Categorias listadas', CategoriaServ.listar_categorias(db))

"API para mostrar una categoría en base a su ID"
@router.get('/{id_categoria}')
def obtener_categoria(id_categoria: int, db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    return respuesta_ok('Categoria encontrada', CategoriaServ.obtener_categoria(db, id_categoria))

"API para actualizar una categoría"
@router.put('/{id_categoria}')
def actualizar_categoria(id_categoria: int, payload: CategoriaUpdate, db: Session = Depends(get_db), user: Usuario = Depends(require_roles('DUENA'))):
    return respuesta_ok('Categoria actualizada', CategoriaServ.actualizar_categoria(db, id_categoria, payload.model_dump(), user.id_usuario))

"API para desactivar 1 categoría"
@router.patch('/{id_categoria}/inactivar')
def inactivar_categoria(id_categoria: int, payload: InactivarPayload, db: Session = Depends(get_db), user: Usuario = Depends(require_roles('DUENA'))):
    return respuesta_ok('Categoria inactivada', CategoriaServ.inactivar_categoria(db, id_categoria, payload.motivo, user.id_usuario))
