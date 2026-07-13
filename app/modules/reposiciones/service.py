from app.modules.productos.model import Producto
from app.modules.proveedores.model import Proveedor
from app.modules.proveedores.repository import ProveedorRepository
from app.modules.reposiciones.repository import ReposicionesRepository
from app.modules.usuarios.model import Usuario
from app.shared.exceptions import DominioError
TRANSICIONES = {
    'BORRADOR': {'SOLICITADA', 'ANULADA'},
    'SOLICITADA': set(),
    'RECIBIDA': {'CERRADA'},
    'CERRADA': set(),
    'ANULADA': set(),
}
"""Clase servicio que ayudará a crear las funciones que permiten el funcionamiento 
de las APIs en el  router de reposiciones"""
class ReposicionesService:
    def __init__(self,db):
        self.repo=ReposicionesRepository(db)
        self.proveedor_repo = ProveedorRepository(db)
        self.db=db
    
    def crear_reposicion(self, payload: dict, user: Usuario) -> dict:
        if not payload['detalles']:
            raise DominioError('REPOSICION_SIN_DETALLE', 'La reposicion debe incluir al menos un detalle', 400)
        proveedor = self.db.get(Proveedor, payload['id_proveedor'])
        if not proveedor or proveedor.estado != 'ACTIVO':
            raise DominioError('PROVEEDOR_NO_ENCONTRADO', 'Proveedor no encontrado o inactivo', 404)
        self._validar_proveedor_contra_categorias_productos(payload['id_proveedor'], payload['detalles'])
        self._validar_stock_maximo_pedido(payload['detalles'])
        repo = self.repo.create_reposicion(payload, user.id_usuario)
        self.db.commit()
        self.db.refresh(repo)
        return self.obtener_reposicion(repo.id_reposicion)
    
    def listar_reposiciones(self) -> list[dict]:
        rows = self.repo.list_reposiciones()
        detalles_por_reposicion = self.repo.list_detalles_by_reposiciones([r.id_reposicion for r in rows])
        return [
            {
                'id_reposicion': r.id_reposicion,
                'codigo_reposicion': r.codigo_reposicion,
                'id_proveedor': r.id_proveedor,
                'estado_reposicion': r.estado_reposicion,
                'observacion': r.observacion,
                'fecha_solicitud': r.fecha_solicitud,
                'fecha_recepcion': r.fecha_recepcion,
                'creado_por': r.creado_por,
                'fecha_creacion': r.fecha_creacion,
                'editado_por': r.editado_por,
                'fecha_edicion': r.fecha_edicion,
                'detalles': self._serialize_detalles(detalles_por_reposicion.get(r.id_reposicion, [])),
            }
            for r in rows
        ]
    
    def obtener_reposicion(self, id_reposicion: int) -> dict:
        r = self.repo.get_reposicion(id_reposicion)
        if not r:
            raise DominioError('REPOSICION_NO_ENCONTRADA', 'Reposicion no encontrada', 404)
        detalles = self.repo.list_detalles(id_reposicion)
        return {
            'id_reposicion': r.id_reposicion,
            'codigo_reposicion': r.codigo_reposicion,
            'id_proveedor': r.id_proveedor,
            'estado_reposicion': r.estado_reposicion,
            'observacion': r.observacion,
            'fecha_solicitud': r.fecha_solicitud,
            'fecha_recepcion': r.fecha_recepcion,
            'creado_por': r.creado_por,
            'fecha_creacion': r.fecha_creacion,
            'editado_por': r.editado_por,
            'fecha_edicion': r.fecha_edicion,
            'detalles': self._serialize_detalles(detalles),
        }

    def editar_reposicion(self, id_reposicion: int, payload: dict, user: Usuario) -> dict:
        r = self.repo.get_reposicion(id_reposicion)
        if not r:
            raise DominioError('REPOSICION_NO_ENCONTRADA', 'Reposicion no encontrada', 404)
        if r.estado_reposicion != 'BORRADOR':
            raise DominioError(
                'TRANSICION_ESTADO_INVALIDA',
                'Solo se puede editar una reposicion en borrador',
                409,
            )
        detalles_activos = [
            d for d in payload['detalles']
            if float(d.get('cantidad_solicitada') or 0) > 0
        ]
        if not detalles_activos:
            raise DominioError('REPOSICION_SIN_DETALLE', 'La reposicion debe incluir al menos un detalle', 400)
        proveedor = self.db.get(Proveedor, payload['id_proveedor'])
        if not proveedor or proveedor.estado != 'ACTIVO':
            raise DominioError('PROVEEDOR_NO_ENCONTRADO', 'Proveedor no encontrado o inactivo', 404)
        payload = {**payload, 'detalles': detalles_activos}
        self._validar_proveedor_contra_categorias_productos(payload['id_proveedor'], payload['detalles'])
        self._validar_stock_maximo_pedido(payload['detalles'])
        self.repo.update_reposicion_borrador(r, payload, user.id_usuario)
        self.db.commit()
        self.db.refresh(r)
        return self.obtener_reposicion(r.id_reposicion)
    
    def cambiar_estado(self, id_reposicion: int, payload: dict, user: Usuario) -> dict:
        r = self.repo.get_reposicion(id_reposicion)
        if not r:
            raise DominioError('REPOSICION_NO_ENCONTRADA', 'Reposicion no encontrada', 404)
        if payload['nuevo_estado'] not in TRANSICIONES.get(r.estado_reposicion, set()):
            raise DominioError('TRANSICION_ESTADO_INVALIDA', 'Transicion de estado no permitida', 409)
        if payload['nuevo_estado'] == 'CERRADA' and not r.fecha_recepcion:
            raise DominioError('TRANSICION_ESTADO_INVALIDA', 'No se puede cerrar sin fecha de recepcion', 409)
        self.repo.set_estado(r, payload['nuevo_estado'], payload.get('observacion'), user.id_usuario)
        self.db.commit()
        self.db.refresh(r)
        return self.obtener_reposicion(r.id_reposicion)
    
    def recibir_reposicion(self, id_reposicion: int, payload: dict, user: Usuario) -> dict:
        r = self.repo.get_reposicion_for_update(id_reposicion)
        if not r:
            raise DominioError('REPOSICION_NO_ENCONTRADA', 'Reposicion no encontrada', 404)
        if r.estado_reposicion != 'SOLICITADA':
            raise DominioError('TRANSICION_ESTADO_INVALIDA', 'Solo se puede recibir una reposicion en estado SOLICITADA', 409)
        if self.repo.has_recepcion_movements(r.codigo_reposicion):
            raise DominioError('REPOSICION_YA_RECIBIDA', 'La reposicion ya tiene movimientos de entrada registrados', 409)
        self._validar_detalles_recepcion(id_reposicion, payload['detalles'])
        self._validar_stock_maximo_recepcion(id_reposicion, payload['detalles'])
        result = self.repo.aplicar_recepcion(r, payload['detalles'], payload.get('observacion'), user.id_usuario)
        if result is None:
            raise DominioError('DETALLE_NO_ENCONTRADO', 'Detalle de reposicion no encontrado', 404)
        if result == 'missing_param':
            raise DominioError('PARAMETRO_INVENTARIO_INVALIDO', 'Producto sin parametro inventario', 400)
        self.db.commit()
        self.db.refresh(r)
        return self.obtener_reposicion(r.id_reposicion)

    def _validar_detalles_recepcion(self, id_reposicion: int, detalles_payload: list[dict]) -> None:
        if not detalles_payload:
            raise DominioError('REPOSICION_SIN_DETALLE', 'La recepcion debe incluir al menos un detalle', 400)

        ids_payload = [int(item['id_detalle_reposicion']) for item in detalles_payload]
        if len(ids_payload) != len(set(ids_payload)):
            raise DominioError('DETALLE_DUPLICADO', 'La recepcion contiene detalles duplicados', 400)

        detalles_actuales = {
            d.id_detalle_reposicion: d
            for d in self.repo.list_detalles(id_reposicion)
            if float(d.cantidad_solicitada or 0) > 0
        }
        if set(ids_payload) != set(detalles_actuales.keys()):
            raise DominioError('DETALLE_NO_COINCIDE', 'La recepcion debe incluir exactamente los detalles de la reposicion', 409)

        for item in detalles_payload:
            detalle = detalles_actuales[int(item['id_detalle_reposicion'])]
            cantidad_recibida = float(item['cantidad_recibida'])
            solicitada = float(detalle.cantidad_solicitada or 0)
            ya_recibida = float(detalle.cantidad_recibida or 0)
            pendiente = solicitada - ya_recibida
            if ya_recibida > 0:
                raise DominioError('DETALLE_YA_RECIBIDO', 'La reposicion ya fue recibida total o parcialmente', 409)
            if cantidad_recibida <= 0:
                raise DominioError('CANTIDAD_RECIBIDA_INVALIDA', 'La cantidad recibida debe ser mayor a cero', 400)
            if cantidad_recibida != pendiente:
                raise DominioError('CANTIDAD_RECIBIDA_INVALIDA', 'La cantidad recibida debe coincidir con la cantidad pendiente', 409)

    def _validar_stock_maximo_recepcion(self, id_reposicion: int, detalles_payload: list[dict]) -> None:
        detalles_actuales = {
            d.id_detalle_reposicion: d
            for d in self.repo.list_detalles(id_reposicion)
        }
        parametros = self.repo.list_parametros_by_productos([
            detalle.id_producto
            for detalle in detalles_actuales.values()
        ])

        for item in detalles_payload:
            detalle = detalles_actuales[int(item['id_detalle_reposicion'])]
            parametro = parametros.get(detalle.id_producto)
            if not parametro:
                continue

            stock_maximo = float(parametro.stock_maximo or 0)
            if stock_maximo <= 0:
                continue

            stock_actual = float(parametro.stock_actual or 0)
            cantidad_recibida = float(item['cantidad_recibida'])
            if stock_actual + cantidad_recibida > stock_maximo:
                raise DominioError(
                    'STOCK_MAXIMO_SUPERADO',
                    'Esta recepción superaría el stock máximo configurado para el producto.',
                    409,
                )

    def _validar_stock_maximo_pedido(self, detalles: list[dict]) -> None:
        parametros = self.repo.list_parametros_by_productos([int(d['id_producto']) for d in detalles])
        for detalle in detalles:
            parametro = parametros.get(int(detalle['id_producto']))
            if not parametro:
                continue

            stock_maximo = float(parametro.stock_maximo or 0)
            if stock_maximo <= 0:
                continue

            stock_actual = float(parametro.stock_actual or 0)
            cantidad_solicitada = float(detalle.get('cantidad_solicitada') or 0)
            if stock_actual + cantidad_solicitada > stock_maximo:
                raise DominioError(
                    'STOCK_MAXIMO_SUPERADO',
                    'Esta reposición superaría el stock máximo configurado para el producto.',
                    409,
                )

    def _validar_proveedor_contra_categorias_productos(self, id_proveedor: int, detalles: list[dict]) -> None:
        categoria_ids_requeridas: set[int] = set()
        for d in detalles:
            producto = self.db.get(Producto, d['id_producto'])
            if not producto:
                raise DominioError('PRODUCTO_NO_ENCONTRADO', f"Producto no encontrado: {d['id_producto']}", 404)
            if not producto.id_categoria:
                raise DominioError(
                    'PRODUCTO_SIN_CATEGORIA',
                    f"El producto {producto.nombre_producto} no tiene categoría asociada.",
                    400,
                )
            categoria_ids_requeridas.add(int(producto.id_categoria))

        categorias_proveedor = set(self.proveedor_repo.list_active_category_ids(id_proveedor))
        if not categoria_ids_requeridas.issubset(categorias_proveedor):
            raise DominioError(
                'PROVEEDOR_CATEGORIA_INVALIDA',
                'El proveedor seleccionado no abastece la categoría del producto.',
                409,
            )

    def _serialize_detalles(self, detalles) -> list[dict]:
        return [
            {
                'id_detalle_reposicion': d.id_detalle_reposicion,
                'id_producto': d.id_producto,
                'cantidad_solicitada': float(d.cantidad_solicitada),
                'cantidad_recibida': float(d.cantidad_recibida),
                'costo_unitario': float(d.costo_unitario),
            }
            for d in detalles
            if float(d.cantidad_solicitada or 0) > 0
        ]
