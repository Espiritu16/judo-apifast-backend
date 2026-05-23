from datetime import timedelta
from app.shared.dates import now_lima_naive
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.modules.inventario.model_movimiento import MovimientoInventario
from app.modules.inventario.model_parametro import ParametroInventario
from app.modules.productos.model import Producto
"Clase repositorio que contendrá funciones que se utilizan en Service de inventario"
class InventarioRepository:
    def __init__(self, db: Session):
        self.db = db
    def list_stock(self, q: str | None = None) -> list[tuple[Producto, ParametroInventario]]:
        stmt = (
            select(Producto, ParametroInventario)
            .join(ParametroInventario, ParametroInventario.id_producto == Producto.id_producto)
            .where(Producto.estado == 'ACTIVO')
        )
        if q:
            stmt = stmt.where(func.lower(Producto.nombre_producto).like(f"%{q.lower()}%"))
        return self.db.execute(stmt).all()
    def get_parametro(self, id_producto: int) -> ParametroInventario | None:
        return self.db.get(ParametroInventario, id_producto)

    def get_ultimo_movimiento(self, id_producto: int) -> MovimientoInventario | None:
        stmt = (
            select(MovimientoInventario)
            .where(MovimientoInventario.id_producto == id_producto)
            .order_by(MovimientoInventario.fecha_movimiento.desc(), MovimientoInventario.id_movimiento.desc())
            .limit(1)
        )
        return self.db.execute(stmt).scalars().first()

    def get_consumo_promedio_diario(self, id_producto: int, dias: int = 30) -> float:
        fecha_inicio = now_lima_naive() - timedelta(days=dias)
        total_salidas = self.db.execute(
            select(func.coalesce(func.sum(MovimientoInventario.cantidad), 0))
            .where(MovimientoInventario.id_producto == id_producto)
            .where(MovimientoInventario.fecha_movimiento >= fecha_inicio)
            .where(MovimientoInventario.tipo_movimiento.in_(['SALIDA', 'MERMA']))
        ).scalar_one()
        return float(total_salidas) / float(dias)

    def update_parametros(self, pi: ParametroInventario, data: dict, user_id: int) -> None:
        pi.stock_minimo = data['stock_minimo']
        pi.stock_maximo = data['stock_maximo']
        pi.consumo_promedio_diario = data['consumo_promedio_diario']
        pi.stock_seguridad = data['stock_seguridad']
        pi.tiempo_reposicion_dias = data['tiempo_reposicion_dias']
        pi.editado_por = user_id
        pi.fecha_edicion = now_lima_naive()
