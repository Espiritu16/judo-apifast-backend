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
    def fetch_valorizacion(self):
        return self.db.execute(
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
        ).all()
    def fetch_rotacion(self):
        salida_case = case(
            (MovimientoInventario.tipo_movimiento.in_(['SALIDA', 'MERMA', 'AJUSTE_NEGATIVO']), MovimientoInventario.cantidad),
            else_=0,
        )
        return self.db.execute(
            select(
                Producto.id_producto,
                Producto.nombre_producto,
                func.coalesce(func.sum(salida_case), 0).label('cantidad_salida'),
                ParametroInventario.stock_actual,
            )
            .join(ParametroInventario, ParametroInventario.id_producto == Producto.id_producto)
            .outerjoin(MovimientoInventario, MovimientoInventario.id_producto == Producto.id_producto)
            .group_by(Producto.id_producto, Producto.nombre_producto, ParametroInventario.stock_actual)
        ).all()
    def fetch_stock_critico(self):
        return self.db.execute(
            select(Producto, ParametroInventario)
            .join(ParametroInventario, ParametroInventario.id_producto == Producto.id_producto)
            .where(Producto.estado == 'ACTIVO')
        ).all()
