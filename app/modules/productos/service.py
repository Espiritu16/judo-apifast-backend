from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.modules.productos import repository
from app.shared.exceptions import DominioError
"""Clase servicio que ayudará a crear las funciones que permiten el funcionamiento 
de las APIs en el  router de productos"""
def crear_producto(db: Session, payload: dict, user_id: int) -> dict:
    try:
        item = repository.create(db, payload, user_id)
        db.commit()
        return {'id_producto': item.id_producto}
    except IntegrityError as exc:
        db.rollback()
        raise DominioError('DATO_DUPLICADO', 'Producto duplicado', 409) from exc
def listar_productos(db: Session) -> list[dict]:
    rows = repository.list_all(db)
    return [
        {
            'id_producto': r.id_producto,
            'codigo_producto': r.codigo_producto,
            'nombre_producto': r.nombre_producto,
            'descripcion': r.descripcion,
            'id_categoria': r.id_categoria,
            'unidad_medida': r.unidad_medida,
            'costo_unitario_actual': float(r.costo_unitario_actual),
            'estado': r.estado,
        }
        for r in rows
    ]
def obtener_producto(db: Session, id_producto: int) -> dict:
    r = repository.get(db, id_producto)
    if not r:
        raise DominioError('PRODUCTO_NO_ENCONTRADO', 'Producto no encontrado', 404)
    return {
        'id_producto': r.id_producto,
        'codigo_producto': r.codigo_producto,
        'nombre_producto': r.nombre_producto,
        'descripcion': r.descripcion,
        'id_categoria': r.id_categoria,
        'unidad_medida': r.unidad_medida,
        'costo_unitario_actual': float(r.costo_unitario_actual),
        'estado': r.estado,
    }
def actualizar_producto(db: Session, id_producto: int, payload: dict, user_id: int) -> dict:
    r = repository.get(db, id_producto)
    if not r:
        raise DominioError('PRODUCTO_NO_ENCONTRADO', 'Producto no encontrado', 404)
    repository.update(db, r, payload, user_id)
    db.commit()
    return {'id_producto': id_producto}
def inactivar_producto(db: Session, id_producto: int, motivo: str, user_id: int) -> dict:
    r = repository.get(db, id_producto)
    if not r:
        raise DominioError('PRODUCTO_NO_ENCONTRADO', 'Producto no encontrado', 404)
    repository.inactivate(db, r, motivo, user_id)
    db.commit()
    return {'id_producto': id_producto}
