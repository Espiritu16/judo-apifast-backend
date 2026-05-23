from decimal import Decimal
from sqlalchemy.orm import Session
from app.modules.inventario.model_movimiento import MovimientoInventario
from app.modules.inventario.model_parametro import ParametroInventario
from app.modules.movimientos.repository import MovimientoRepository
from app.modules.productos.model import Producto
from app.modules.usuarios.model import Usuario
from app.shared.exceptions import DominioError
"""Clase servicio que ayudará a crear las funciones que permiten el funcionamiento 
de las APIs en el  router de inventario"""
TIPOS_VALIDOS = {'ENTRADA', 'SALIDA', 'MERMA', 'AJUSTE_POSITIVO', 'AJUSTE_NEGATIVO'}


class MovimientoService:
    def __init__(self,db:Session):
        self.repo=MovimientoRepository(db)
        self.db=db
    def registrar_movimiento(self, payload: dict, user: Usuario) -> MovimientoInventario:
        tipo = payload['tipo_movimiento']
        if tipo not in TIPOS_VALIDOS:
            raise DominioError('MOVIMIENTO_INVALIDO', 'Tipo de movimiento no valido', 400)
        if tipo == 'ENTRADA' and payload.get('costo_unitario') is None:
            raise DominioError('COSTO_REQUERIDO', 'costo_unitario es obligatorio para ENTRADA', 400)
        producto = self.db.get(Producto, payload['id_producto'])
        if not producto or producto.estado != 'ACTIVO':
            raise DominioError('PRODUCTO_NO_ENCONTRADO', 'Producto no encontrado o inactivo', 404)
        parametro = self.db.get(ParametroInventario, payload['id_producto'])
        if not parametro:
            parametro = ParametroInventario(
                id_producto=payload['id_producto'],
                stock_actual=0,
                stock_minimo=0,
                stock_maximo=0,
                consumo_promedio_diario=0,
                stock_seguridad=0,
                tiempo_reposicion_dias=0,
                creado_por=user.id_usuario,
            )
            self.db.add(parametro)
            self.db.flush()
        cantidad = Decimal(str(payload['cantidad']))
        stock_actual = Decimal(str(parametro.stock_actual))
        stock_seguridad = Decimal(str(parametro.stock_seguridad or 0))
        if tipo == 'ENTRADA':
            costo_unitario = Decimal(str(payload.get('costo_unitario') or 0))
            precio_venta_producto = Decimal(str(producto.costo_unitario_actual or 0))
            if precio_venta_producto > 0 and costo_unitario > precio_venta_producto:
                raise DominioError(
                    'COSTO_SUPERA_PRECIO_VENTA',
                    'El costo unitario de entrada no puede ser mayor al precio de venta del producto.',
                    400
                )
        if tipo in {'SALIDA', 'MERMA', 'AJUSTE_NEGATIVO'} and stock_actual - cantidad < 0:
            raise DominioError(
                'STOCK_INSUFICIENTE',
                'No hay stock suficiente para realizar la operacion',
                409
            )
        if tipo in {'SALIDA', 'MERMA', 'AJUSTE_NEGATIVO'} and stock_actual - cantidad < stock_seguridad:
            raise DominioError(
                'STOCK_SEGURIDAD_VIOLADA',
                'La operación invade el stock de seguridad configurado para este producto.',
                409
            )
        if tipo in {'ENTRADA', 'AJUSTE_POSITIVO'}:
            parametro.stock_actual = stock_actual + cantidad
        else:
            parametro.stock_actual = stock_actual - cantidad
        if tipo == 'ENTRADA' and payload.get('costo_unitario') is not None:
            producto.costo_unitario_actual = payload['costo_unitario']
        movimiento = MovimientoInventario(
            id_producto=payload['id_producto'],
            tipo_movimiento=tipo,
            cantidad=payload['cantidad'],
            costo_unitario=payload.get('costo_unitario'),
            motivo=payload['motivo'],
            referencia=payload.get('referencia'),
            observacion=payload.get('observacion'),
            creado_por=user.id_usuario,
        )
        self.db.add(movimiento)
        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        self.db.refresh(movimiento)
        return movimiento
    def listar_movimientos(self) -> list[dict]:
        data = self.repo.list_all()
        return [
            {
                'id_movimiento': m.id_movimiento,
                'id_producto': m.id_producto,
                'fecha_movimiento': m.fecha_movimiento,
                'tipo_movimiento': m.tipo_movimiento,
                'cantidad': float(m.cantidad),
                'costo_unitario': float(m.costo_unitario) if m.costo_unitario is not None else None,
                'motivo': m.motivo,
                'referencia': m.referencia,
                'observacion': m.observacion,
                'creado_por': m.creado_por,
                'fecha_creacion': m.fecha_creacion,
                'editado_por': m.editado_por,
                'fecha_edicion': m.fecha_edicion,
            }
            for m in data
        ]
    def obtener_movimiento(self, id_movimiento: int) -> dict | None:
        m = self.repo.get(id_movimiento)
        if not m:
            raise DominioError('RESOURCE_NOT_FOUND', 'Movimiento no encontrado.', 404)
        return {
            'id_movimiento': m.id_movimiento,
            'id_producto': m.id_producto,
            'fecha_movimiento': m.fecha_movimiento,
            'tipo_movimiento': m.tipo_movimiento,
            'cantidad': float(m.cantidad),
            'costo_unitario': float(m.costo_unitario) if m.costo_unitario is not None else None,
            'motivo': m.motivo,
            'referencia': m.referencia,
            'observacion': m.observacion,
            'creado_por': m.creado_por,
            'fecha_creacion': m.fecha_creacion,
            'editado_por': m.editado_por,
            'fecha_edicion': m.fecha_edicion,
        }
