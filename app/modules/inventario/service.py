from sqlalchemy.orm import Session
from app.modules.inventario import repository
from app.shared.exceptions import DominioError
"Clase servicio que ayudará a crear las APIs en el  router de inventario"
def consultar_stock(db: Session, q: str | None = None) -> list[dict]:
    rows = repository.list_stock(db)
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
def stock_critico(db: Session) -> list[dict]:
    rows = repository.list_stock(db)
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

def actualizar_parametros(db: Session, id_producto: int, payload: dict, user_id: int) -> dict:
    if payload['stock_maximo'] < payload['stock_minimo']:
        raise DominioError('PARAMETRO_INVENTARIO_INVALIDO', 'stock_maximo no puede ser menor a stock_minimo', 400)

    pi = repository.get_parametro(db, id_producto)
    if not pi:
        raise DominioError('PRODUCTO_NO_ENCONTRADO', 'No existe parametro de inventario para este producto', 404)
    repository.update_parametros(db, pi, payload, user_id)
    db.commit()
    return {'id_producto': id_producto}