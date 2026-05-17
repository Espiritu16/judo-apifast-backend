from sqlalchemy import select
from sqlalchemy.orm import Session
from app.modules.inventario.model_movimiento import MovimientoInventario
"Clase repositorio que contendrá funciones que se utilizan en Service de movimiento"
class MovimientoRepository:
    def __init__(self,db:Session):
        self.db=db
    def list_all(self) -> list[MovimientoInventario]:
        return self.db.execute(select(MovimientoInventario).order_by(MovimientoInventario.id_movimiento.desc())).scalars().all()
    def get(self, id_movimiento: int) -> MovimientoInventario | None:
        return self.db.get(MovimientoInventario, id_movimiento)