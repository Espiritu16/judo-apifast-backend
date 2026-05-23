from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.deps import get_db, require_roles
from app.modules.usuarios.model import Usuario
from app.modules.usuarios.schema import UsuarioCreate, UsuarioEstadoUpdate, UsuarioUpdate
from app.modules.usuarios.service import UsuarioService
from app.shared.responses import respuesta_ok


router = APIRouter()


@router.get('')
def listar_usuarios(db: Session = Depends(get_db), _: Usuario = Depends(require_roles('DUEÑA'))):
    return respuesta_ok('Usuarios listados', UsuarioService(db).listar_usuarios())


@router.get('/roles')
def listar_roles(db: Session = Depends(get_db), _: Usuario = Depends(require_roles('DUEÑA'))):
    return respuesta_ok('Roles listados', UsuarioService(db).listar_roles())


@router.get('/{id_usuario}')
def obtener_usuario(id_usuario: int, db: Session = Depends(get_db), _: Usuario = Depends(require_roles('DUEÑA'))):
    return respuesta_ok('Usuario encontrado', UsuarioService(db).obtener_usuario(id_usuario))


@router.post('')
def crear_usuario(payload: UsuarioCreate, db: Session = Depends(get_db), actor: Usuario = Depends(require_roles('DUEÑA'))):
    return respuesta_ok('Usuario creado', UsuarioService(db).crear_usuario(payload.model_dump(), actor.id_usuario))


@router.put('/{id_usuario}')
def actualizar_usuario(id_usuario: int, payload: UsuarioUpdate, db: Session = Depends(get_db), actor: Usuario = Depends(require_roles('DUEÑA'))):
    return respuesta_ok('Usuario actualizado', UsuarioService(db).actualizar_usuario(id_usuario, payload.model_dump(), actor.id_usuario))


@router.patch('/{id_usuario}/estado')
def actualizar_estado_usuario(id_usuario: int, payload: UsuarioEstadoUpdate, db: Session = Depends(get_db), actor: Usuario = Depends(require_roles('DUEÑA'))):
    return respuesta_ok(
        'Estado de usuario actualizado',
        UsuarioService(db).actualizar_estado(id_usuario, payload.estado, payload.motivo, actor.id_usuario),
    )
