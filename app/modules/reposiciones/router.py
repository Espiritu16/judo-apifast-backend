from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.deps import get_current_user, get_db, require_roles
from app.modules.reposiciones.schema import ReposicionCreate, ReposicionEstadoUpdate, ReposicionUpdate, RecibirReposicionIn
from app.modules.reposiciones.service import ReposicionesService as ReposicionesServ
from app.modules.usuarios.model import Usuario
from app.shared.responses import respuesta_ok
router = APIRouter()
#API para registrar una reposición
@router.post('')
def crear_reposicion(payload: ReposicionCreate, db: Session = Depends(get_db), user: Usuario = Depends(require_roles('DUEÑA', 'EMPLEADO'))):
    return respuesta_ok('Reposicion creada', ReposicionesServ(db).crear_reposicion(payload.model_dump(), user))
#API para mostrar datos de las reposiciones registradas
@router.get('')
def listar_reposiciones(db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    return respuesta_ok('Reposiciones listadas', ReposicionesServ(db).listar_reposiciones())
#API para mostrar datos de una reposición registrada usando su ID
@router.get('/{id_reposicion}')
def obtener_reposicion(id_reposicion: int, db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    return respuesta_ok('Reposicion encontrada', ReposicionesServ(db).obtener_reposicion(id_reposicion))
#API para editar una reposición en borrador
@router.put('/{id_reposicion}')
def editar_reposicion(id_reposicion: int, payload: ReposicionUpdate, db: Session = Depends(get_db), user: Usuario = Depends(require_roles('DUEÑA', 'EMPLEADO'))):
    return respuesta_ok('Reposicion actualizada', ReposicionesServ(db).editar_reposicion(id_reposicion, payload.model_dump(), user))
#API para cambiar el estado de una reposición registrada
@router.patch('/{id_reposicion}/estado')
def cambiar_estado_reposicion(id_reposicion: int, payload: ReposicionEstadoUpdate, db: Session = Depends(get_db), user: Usuario = Depends(require_roles('DUEÑA', 'EMPLEADO'))):
    return respuesta_ok('Estado actualizado', ReposicionesServ(db).cambiar_estado(id_reposicion, payload.model_dump(), user))
#API para marcar una reposición como recibida y actualizar el stock
@router.post('/{id_reposicion}/recibir')
def recibir_reposicion(id_reposicion: int, payload: RecibirReposicionIn, db: Session = Depends(get_db), user: Usuario = Depends(require_roles('DUEÑA', 'EMPLEADO'))):
    return respuesta_ok('Reposicion recibida y stock actualizado', ReposicionesServ(db).recibir_reposicion(id_reposicion, payload.model_dump(), user))
