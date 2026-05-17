from sqlalchemy import select
from sqlalchemy.orm import Session
from app.modules.inventario.model_movimiento import MovimientoInventario
"Clase repositorio que contendrá funciones que se utilizan en Service de movimiento"
def list_all(db: Session) -> list[MovimientoInventario]:
    return db.execute(select(MovimientoInventario).order_by(MovimientoInventario.id_movimiento.desc())).scalars().all()
def get(db: Session, id_movimiento: int) -> MovimientoInventario | None:
    return db.get(MovimientoInventario, id_movimiento)