from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.modules.categorias.model import Categoria
"Clase repositorio que contendrá funciones que se utilizan en Service de Categoría"
def create(db: Session, data: dict, creado_por: int) -> Categoria:
    item = Categoria(**data, creado_por=creado_por)
    db.add(item)
    db.flush()
    db.refresh(item)
    return item
def list_all(db: Session) -> list[Categoria]:
    return db.execute(select(Categoria).order_by(Categoria.id_categoria.desc())).scalars().all()
def get(db: Session, id_categoria: int) -> Categoria | None:
    return db.get(Categoria, id_categoria)
def update(db: Session, item: Categoria, data: dict, user_id: int) -> Categoria:
    for k, v in data.items():
        setattr(item, k, v)
    item.editado_por = user_id
    item.fecha_edicion = datetime.utcnow()
    return item
def inactivate(db: Session, item: Categoria, motivo: str, user_id: int) -> Categoria:
    item.estado = 'INACTIVO'
    item.inactivado_por = user_id
    item.motivo_inactivacion = motivo
    item.fecha_inactivacion = datetime.utcnow()
    return item
