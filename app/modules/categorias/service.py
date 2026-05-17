from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.modules.categorias import repository
from app.shared.exceptions import DominioError
"Clase servicio que ayudará a crear las APIs en el  router de categoría"
def crear_categoria(db: Session, payload: dict, user_id: int) -> dict:
    try:
        item = repository.create(db, payload, user_id)
        db.commit()
        return {'id_categoria': item.id_categoria}
    except IntegrityError as exc:
        db.rollback()
        raise DominioError('DATO_DUPLICADO', 'Categoria duplicada', 409) from exc
def listar_categorias(db: Session) -> list[dict]:
    rows = repository.list_all(db)
    return [
        {'id_categoria': r.id_categoria, 'nombre_categoria': r.nombre_categoria, 'descripcion': r.descripcion, 'estado': r.estado}
        for r in rows
    ]
def obtener_categoria(db: Session, id_categoria: int) -> dict:
    r = repository.get(db, id_categoria)
    if not r:
        raise DominioError('CATEGORIA_NO_ENCONTRADA', 'Categoria no encontrada', 404)
    return {'id_categoria': r.id_categoria, 'nombre_categoria': r.nombre_categoria, 'descripcion': r.descripcion, 'estado': r.estado}
def actualizar_categoria(db: Session, id_categoria: int, payload: dict, user_id: int) -> dict:
    r = repository.get(db, id_categoria)
    if not r:
        raise DominioError('CATEGORIA_NO_ENCONTRADA', 'Categoria no encontrada', 404)
    repository.update(db, r, payload, user_id)
    db.commit()
    return {'id_categoria': id_categoria}
def inactivar_categoria(db: Session, id_categoria: int, motivo: str, user_id: int) -> dict:
    r = repository.get(db, id_categoria)
    if not r:
        raise DominioError('CATEGORIA_NO_ENCONTRADA', 'Categoria no encontrada', 404)
    repository.inactivate(db, r, motivo, user_id)
    db.commit()
    return {'id_categoria': id_categoria}
