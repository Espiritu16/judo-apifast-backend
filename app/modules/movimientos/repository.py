from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.modules.productos.model import Producto
from app.modules.inventario.model_movimiento import MovimientoInventario
"Clase repositorio que contendrá funciones que se utilizan en Service de movimiento"
class MovimientoRepository:
    def __init__(self,db:Session):
        self.db=db
    def list_all(
        self,
        desde: datetime | None = None,
        hasta: datetime | None = None,
        tipo: str | None = None,
        producto_id: int | None = None,
        categoria_id: int | None = None,
    ) -> list[MovimientoInventario]:
        stmt = select(MovimientoInventario).join(
            Producto, Producto.id_producto == MovimientoInventario.id_producto
        )
        if desde:
            stmt = stmt.where(MovimientoInventario.fecha_movimiento >= desde)
        if hasta:
            stmt = stmt.where(MovimientoInventario.fecha_movimiento <= hasta)
        if tipo:
            stmt = stmt.where(MovimientoInventario.tipo_movimiento == tipo)
        if producto_id:
            stmt = stmt.where(MovimientoInventario.id_producto == producto_id)
        if categoria_id:
            stmt = stmt.where(Producto.id_categoria == categoria_id)
        stmt = stmt.order_by(MovimientoInventario.id_movimiento.desc())
        return self.db.execute(stmt).scalars().all()

    def get(self, id_movimiento: int) -> MovimientoInventario | None:
        return self.db.get(MovimientoInventario, id_movimiento)
