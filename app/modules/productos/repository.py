from app.shared.dates import now_lima_naive
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.modules.inventario.model_parametro import ParametroInventario
from app.modules.productos.model import Producto
"Clase repositorio que contendrá funciones que se utilizan en Service de productos"
class ProductosRepository:
    def __init__(self, db: Session):
        self.db = db
    def create(self, data: dict, user_id: int) -> Producto:
        item = Producto(**data, creado_por=user_id)
        self.db.add(item)
        self.db.flush()
        self.db.add(
            ParametroInventario(
                id_producto=item.id_producto,
                stock_actual=0,
                stock_minimo=0,
                stock_maximo=0,
                consumo_promedio_diario=0,
                stock_seguridad=0,
                tiempo_reposicion_dias=0,
                creado_por=user_id,
            )
        )
        self.db.refresh(item)
        return item
    def list_all(self) -> list[Producto]:
        return self.db.execute(select(Producto).order_by(Producto.id_producto.desc())).scalars().all()
    def get(self, id_producto: int) -> Producto | None:
        return self.db.get(Producto, id_producto)
    def update(self, item: Producto, data: dict, user_id: int) -> Producto:
        for k, v in data.items():
            setattr(item, k, v)
        item.editado_por = user_id
        item.fecha_edicion = now_lima_naive()
        return item
    def inactivate(self, item: Producto, motivo: str, user_id: int) -> Producto:
        item.estado = 'INACTIVO'
        item.inactivado_por = user_id
        item.motivo_inactivacion = motivo
        item.fecha_inactivacion = now_lima_naive()
        return item