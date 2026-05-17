from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import Session
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
            stmt = stmt.where(Producto.nombre_producto.ilike(f"%{q}%"))  
        return self.db.execute(stmt).all()
    def get_parametro(self, id_producto: int) -> ParametroInventario | None:
        return self.db.get(ParametroInventario, id_producto)
    def update_parametros(self, pi: ParametroInventario, data: dict, user_id: int) -> None:
        pi.stock_minimo = data['stock_minimo']
        pi.stock_maximo = data['stock_maximo']
        pi.consumo_promedio_diario = data['consumo_promedio_diario']
        pi.stock_seguridad = data['stock_seguridad']
        pi.tiempo_reposicion_dias = data['tiempo_reposicion_dias']
        pi.editado_por = user_id
        pi.fecha_edicion = datetime.utcnow()
