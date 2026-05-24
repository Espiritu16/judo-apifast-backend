from datetime import date, datetime, time
from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.modules.categorias.model import Categoria
from app.modules.inventario.model_movimiento import MovimientoInventario
from app.modules.inventario.model_parametro import ParametroInventario
from app.modules.productos.model import Producto
"Clase repositorio que contendrá funciones que se utilizan en Service de reportes"
class ReportesRepository:
    def __init__(self,db:Session):
        self.db=db
    def _parse_rango(self, desde: date | None, hasta: date | None) -> tuple[datetime | None, datetime | None]:
        if not desde and not hasta:
            return None, None
        from_dt = datetime.combine(desde, time.min) if desde else None
        to_dt = datetime.combine(hasta, time.max) if hasta else None
        return from_dt, to_dt

    def fetch_valorizacion(self, desde: date | None = None, hasta: date | None = None):
        from_dt, to_dt = self._parse_rango(desde, hasta)
        has_mov_in_range = (
            select(func.count(MovimientoInventario.id_movimiento))
            .where(MovimientoInventario.id_producto == Producto.id_producto)
        )
        if from_dt:
            has_mov_in_range = has_mov_in_range.where(MovimientoInventario.fecha_movimiento >= from_dt)
        if to_dt:
            has_mov_in_range = has_mov_in_range.where(MovimientoInventario.fecha_movimiento <= to_dt)

        stmt = (
            select(
                Producto.id_producto,
                Producto.nombre_producto,
                Categoria.nombre_categoria,
                ParametroInventario.stock_actual,
                Producto.costo_unitario_actual,
                (ParametroInventario.stock_actual * Producto.costo_unitario_actual).label('valor_producto'),
            )
            .join(Categoria, Categoria.id_categoria == Producto.id_categoria)
            .join(ParametroInventario, ParametroInventario.id_producto == Producto.id_producto)
            .where(Producto.estado == 'ACTIVO')
        )
        if from_dt or to_dt:
            stmt = stmt.where(has_mov_in_range.scalar_subquery() > 0)

        return self.db.execute(stmt).all()
    def fetch_rotacion(self, desde: date | None = None, hasta: date | None = None):
        from_dt, to_dt = self._parse_rango(desde, hasta)
        salida_case = case(
            (MovimientoInventario.tipo_movimiento.in_(['SALIDA', 'MERMA', 'AJUSTE_NEGATIVO']), MovimientoInventario.cantidad),
            else_=0,
        )
        stmt = (
            select(
                Producto.id_producto,
                Producto.nombre_producto,
                Producto.id_categoria,
                Categoria.nombre_categoria,
                func.coalesce(func.sum(salida_case), 0).label('cantidad_salida'),
                ParametroInventario.stock_actual,
            )
            .join(Categoria, Categoria.id_categoria == Producto.id_categoria)
            .join(ParametroInventario, ParametroInventario.id_producto == Producto.id_producto)
            .outerjoin(MovimientoInventario, MovimientoInventario.id_producto == Producto.id_producto)
            .group_by(
                Producto.id_producto,
                Producto.nombre_producto,
                Producto.id_categoria,
                Categoria.nombre_categoria,
                ParametroInventario.stock_actual
            )
        )
        if from_dt:
            stmt = stmt.where(
                (MovimientoInventario.id_movimiento.is_(None))
                | (MovimientoInventario.fecha_movimiento >= from_dt)
            )
        if to_dt:
            stmt = stmt.where(
                (MovimientoInventario.id_movimiento.is_(None))
                | (MovimientoInventario.fecha_movimiento <= to_dt)
            )
        return self.db.execute(stmt).all()

    def fetch_stock_critico(self, desde: date | None = None, hasta: date | None = None):
        from_dt, to_dt = self._parse_rango(desde, hasta)
        stmt = (
            select(Producto, ParametroInventario)
            .join(ParametroInventario, ParametroInventario.id_producto == Producto.id_producto)
            .where(Producto.estado == 'ACTIVO')
        )
        if from_dt or to_dt:
            has_mov_in_range = (
                select(func.count(MovimientoInventario.id_movimiento))
                .where(MovimientoInventario.id_producto == Producto.id_producto)
            )
            if from_dt:
                has_mov_in_range = has_mov_in_range.where(MovimientoInventario.fecha_movimiento >= from_dt)
            if to_dt:
                has_mov_in_range = has_mov_in_range.where(MovimientoInventario.fecha_movimiento <= to_dt)
            stmt = stmt.where(has_mov_in_range.scalar_subquery() > 0)

        return self.db.execute(
            stmt
        ).all()
