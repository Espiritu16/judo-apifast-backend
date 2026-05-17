from sqlalchemy.orm import Session
from app.modules.inventario.repository import InventarioRepository
from app.shared.exceptions import DominioError
"Clase servicio que ayudará a crear las APIs en el  router de inventario"
class InventarioService:
    def __init__(self, db: Session):
        """Inicializa el repositorio compartiendo la misma sesión de BD."""
        self.repo = InventarioRepository(db)
        self.db = db
    def consultar_stock(self, q: str | None = None) -> list[dict]:
        rows = self.repo.list_stock()
        data = []
        for p, pi in rows:
            if q and q.lower() not in p.nombre_producto.lower():
                continue
            data.append(
                {
                    'id_producto': p.id_producto,
                    'nombre_producto': p.nombre_producto,
                    'stock_actual': float(pi.stock_actual),
                    'stock_minimo': float(pi.stock_minimo),
                    'stock_maximo': float(pi.stock_maximo),
                }
            )
        return data
    def stock_critico(self) -> list[dict]:
        rows = self.repo.list_stock()
        data = []
        for p, pi in rows:
            actual = float(pi.stock_actual)
            minimo = float(pi.stock_minimo)
            maximo = float(pi.stock_maximo)
            if actual <= minimo:
                sugerida = max(0.0, (maximo - actual)) if maximo > 0 else max(0.0, float(pi.punto_reorden) - actual)
                data.append(
                    {
                        'id_producto': p.id_producto,
                        'nombre_producto': p.nombre_producto,
                        'stock_actual': actual,
                        'stock_minimo': minimo,
                        'stock_maximo': maximo,
                        'cantidad_sugerida': sugerida,
                    }
                )
        return data
    def actualizar_parametros(self, id_producto: int, payload: dict, user_id: int) -> dict:
        if payload['stock_maximo'] < payload['stock_minimo']:
            raise DominioError(
                'PARAMETRO_INVENTARIO_INVALIDO', 
                'stock_maximo no puede ser menor a stock_minimo', 
                400
            )
        pi = self.repo.get_parametro(id_producto)
        if not pi:
            raise DominioError(
                'PRODUCTO_NO_ENCONTRADO', 
                'No existe parametro de inventario para este producto', 
                404
            )
        self.repo.update_parametros(pi, payload, user_id)
        self.db.commit()  # El servicio controla cuándo se confirma la transacción
        return {'id_producto': id_producto}