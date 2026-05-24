from sqlalchemy.orm import Session
from app.modules.productos.model import Producto
from app.modules.proveedores.model import Proveedor
from app.modules.proveedores.repository import ProveedorRepository
from app.modules.reposiciones.repository import ReposicionesRepository
from app.modules.usuarios.model import Usuario
from app.shared.exceptions import DominioError
TRANSICIONES = {
    'BORRADOR': {'SOLICITADA', 'ANULADA'},
    'SOLICITADA': {'RECIBIDA', 'ANULADA'},
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
        repo = self.repo.create_reposicion(payload, user.id_usuario)
        self.db.commit()
        self.db.refresh(repo)
        return self.obtener_reposicion(repo.id_reposicion)
    
    def listar_reposiciones(self) -> list[dict]:
        rows = self.repo.list_reposiciones()
        return [
            {
                'id_reposicion': r.id_reposicion,
                'codigo_reposicion': r.codigo_reposicion,
                'id_proveedor': r.id_proveedor,
                'estado_reposicion': r.estado_reposicion,
                'fecha_solicitud': r.fecha_solicitud,
                'fecha_recepcion': r.fecha_recepcion,
                'creado_por': r.creado_por,
                'fecha_creacion': r.fecha_creacion,
                'editado_por': r.editado_por,
                'fecha_edicion': r.fecha_edicion,
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
            'detalles': [
                {
                    'id_detalle_reposicion': d.id_detalle_reposicion,
                    'id_producto': d.id_producto,
                    'cantidad_solicitada': float(d.cantidad_solicitada),
                    'cantidad_recibida': float(d.cantidad_recibida),
                }
                for d in detalles
            ],
        }
    
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
        r = self.repo.get_reposicion(id_reposicion)
        if not r:
            raise DominioError('REPOSICION_NO_ENCONTRADA', 'Reposicion no encontrada', 404)
        if r.estado_reposicion != 'SOLICITADA':
            raise DominioError('TRANSICION_ESTADO_INVALIDA', 'Solo se puede recibir una reposicion en estado SOLICITADA', 409)
        result = self.repo.aplicar_recepcion(r, payload['detalles'], payload.get('observacion'), user.id_usuario)
        if result is None:
            raise DominioError('DETALLE_NO_ENCONTRADO', 'Detalle de reposicion no encontrado', 404)
        if result == 'missing_param':
            raise DominioError('PARAMETRO_INVENTARIO_INVALIDO', 'Producto sin parametro inventario', 400)
        self.db.commit()
        self.db.refresh(r)
        return self.obtener_reposicion(r.id_reposicion)

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
