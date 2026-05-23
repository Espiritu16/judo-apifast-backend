from sqlalchemy.orm import Session
from app.modules.inventario.repository import InventarioRepository
from app.shared.exceptions import DominioError


class InventarioService:
    def __init__(self, db: Session):
        self.repo = InventarioRepository(db)
        self.db = db

    def consultar_stock(self, q: str | None = None) -> list[dict]:
        rows = self.repo.list_stock()
        data = []
        for p, pi in rows:
            if q and q.lower() not in p.nombre_producto.lower():
                continue
            ultimo = self.repo.get_ultimo_movimiento(p.id_producto)
            data.append(
                {
                    'id_producto': p.id_producto,
                    'nombre_producto': p.nombre_producto,
                    'stock_actual': float(pi.stock_actual),
                    'stock_minimo': float(pi.stock_minimo),
                    'stock_maximo': float(pi.stock_maximo),
                    'stock_seguridad': float(pi.stock_seguridad),
                    'estado_stock': pi.estado_stock,
                    'ultimo_movimiento': (
                        ultimo.fecha_movimiento.isoformat(sep=' ', timespec='minutes')
                        if ultimo and getattr(ultimo, 'fecha_movimiento', None)
                        else None
                    ),
                    'tipo_ultimo_movimiento': (
                        ultimo.tipo_movimiento
                        if ultimo
                        else None
                    ),
                    'cantidad_ultimo_movimiento': (
                        float(ultimo.cantidad)
                        if ultimo and getattr(ultimo, 'cantidad', None) is not None
                        else None
                    ),
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
                        'estado_stock': pi.estado_stock,
                        'cantidad_sugerida': sugerida,
                    }
                )
        return data

    def actualizar_parametros(self, id_producto: int, payload: dict, user_id: int) -> dict:
        self._validar_payload(payload)

        pi = self.repo.get_parametro(id_producto)
        if not pi:
            raise DominioError('RESOURCE_NOT_FOUND', 'No existe parámetro de inventario para este producto.', 404)

        if self._is_same_parametro(pi, payload):
            raise DominioError('NO_CHANGES_DETECTED', 'No se detectaron cambios para guardar.', 400)

        payload_ajustado = dict(payload)
        if payload_ajustado.get('consumo_promedio_diario') is None:
            payload_ajustado['consumo_promedio_diario'] = self.repo.get_consumo_promedio_diario(id_producto, dias=30)
        if payload_ajustado.get('tiempo_reposicion_dias') is None:
            actual = int(pi.tiempo_reposicion_dias or 0)
            payload_ajustado['tiempo_reposicion_dias'] = actual if actual > 0 else 7

        self.repo.update_parametros(pi, payload_ajustado, user_id)
        self.db.commit()
        self.db.refresh(pi)
        return {
            'id_producto': pi.id_producto,
            'stock_actual': float(pi.stock_actual),
            'stock_minimo': float(pi.stock_minimo),
            'stock_maximo': float(pi.stock_maximo),
            'stock_seguridad': float(pi.stock_seguridad),
            'estado_stock': pi.estado_stock,
            'ultimo_movimiento': '',
        }

    def _validar_payload(self, payload: dict) -> None:
        required = ('stock_minimo', 'stock_maximo', 'stock_seguridad')
        for key in required:
            if payload.get(key) is None:
                raise DominioError('VALIDATION_ERROR', f'El campo {key} es obligatorio.', 400)
            if float(payload[key]) < 0:
                raise DominioError('VALIDATION_ERROR', f'El campo {key} no puede ser negativo.', 400)

        if float(payload['stock_maximo']) <= float(payload['stock_minimo']):
            raise DominioError('VALIDATION_ERROR', 'stock_maximo debe ser mayor que stock_minimo.', 400)

    def _is_same_parametro(self, actual, payload: dict) -> bool:
        return (
            float(actual.stock_minimo) == float(payload.get('stock_minimo'))
            and float(actual.stock_maximo) == float(payload.get('stock_maximo'))
            and float(actual.stock_seguridad) == float(payload.get('stock_seguridad'))
        )
