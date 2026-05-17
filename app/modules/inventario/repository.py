from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.modules.inventario.model_parametro import ParametroInventario
from app.modules.productos.model import Producto
"Clase repositorio que contendrá funciones que se utilizan en Service de inventario"
def list_stock(db: Session) -> list[tuple[Producto, ParametroInventario]]:
    return db.execute(
        select(Producto, ParametroInventario)
        .join(ParametroInventario, ParametroInventario.id_producto == Producto.id_producto)
        .where(Producto.estado == 'ACTIVO')
    ).all()
def get_parametro(db: Session, id_producto: int) -> ParametroInventario | None:
    return db.get(ParametroInventario, id_producto)
def update_parametros(db: Session, pi: ParametroInventario, data: dict, user_id: int) -> None:
    pi.stock_minimo = data['stock_minimo']
    pi.stock_maximo = data['stock_maximo']
    pi.consumo_promedio_diario = data['consumo_promedio_diario']
    pi.stock_seguridad = data['stock_seguridad']
    pi.tiempo_reposicion_dias = data['tiempo_reposicion_dias']
    pi.editado_por = user_id
    pi.fecha_edicion = datetime.utcnow()
