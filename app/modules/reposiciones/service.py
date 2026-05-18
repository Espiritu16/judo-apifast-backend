from sqlalchemy.orm import Session
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
        self.db=db
    
    def crear_reposicion(self, payload: dict, user: Usuario) -> dict:
        if not payload['detalles']:
            raise DominioError('REPOSICION_SIN_DETALLE', 'La reposicion debe incluir al menos un detalle', 400)
        repo = self.repo.create_reposicion(self.db, payload, user.id_usuario)
        self.db.commit()
        return {'id_reposicion': repo.id_reposicion}
    
    def listar_reposiciones(self) -> list[dict]:
        rows = self.repo.list_reposiciones(self.db)
        return [
            {
                'id_reposicion': r.id_reposicion,
                'codigo_reposicion': r.codigo_reposicion,
                'id_proveedor': r.id_proveedor,
                'estado_reposicion': r.estado_reposicion,
                'fecha_solicitud': r.fecha_solicitud,
                'fecha_recepcion': r.fecha_recepcion,
            }
            for r in rows
        ]
    
    def obtener_reposicion(self, id_reposicion: int) -> dict:
        r = self.repo.get_reposicion(self.db, id_reposicion)
        if not r:
            raise DominioError('REPOSICION_NO_ENCONTRADA', 'Reposicion no encontrada', 404)
        detalles = self.repo.list_detalles(self.db, id_reposicion)
        return {
            'id_reposicion': r.id_reposicion,
            'codigo_reposicion': r.codigo_reposicion,
            'estado_reposicion': r.estado_reposicion,
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
        r = self.repo.get_reposicion(self.db, id_reposicion)
        if not r:
            raise DominioError('REPOSICION_NO_ENCONTRADA', 'Reposicion no encontrada', 404)
        if payload['nuevo_estado'] not in TRANSICIONES.get(r.estado_reposicion, set()):
            raise DominioError('TRANSICION_ESTADO_INVALIDA', 'Transicion de estado no permitida', 409)
        if payload['nuevo_estado'] in {'ANULADA', 'CERRADA'} and user.rol != 'DUENA':
            raise DominioError('USUARIO_NO_AUTORIZADO', 'Solo DUENA puede anular/cerrar reposiciones', 403)
        self.repo.set_estado(r, payload['nuevo_estado'], payload.get('observacion'), user.id_usuario)
        self.db.commit()
        return {'id_reposicion': r.id_reposicion, 'estado_reposicion': r.estado_reposicion}
    
    def recibir_reposicion(self, id_reposicion: int, payload: dict, user: Usuario) -> dict:
        r = self.repo.get_reposicion(self.db, id_reposicion)
        if not r:
            raise DominioError('REPOSICION_NO_ENCONTRADA', 'Reposicion no encontrada', 404)
        if r.estado_reposicion not in {'SOLICITADA', 'RECIBIDA'}:
            raise DominioError('TRANSICION_ESTADO_INVALIDA', 'Solo se puede recibir una reposicion solicitada/recibida', 409)
        result = self.repo.aplicar_recepcion(self.db, r, payload['detalles'], payload.get('observacion'), user.id_usuario)
        if result is None:
            raise DominioError('DETALLE_NO_ENCONTRADO', 'Detalle de reposicion no encontrado', 404)
        if result == 'missing_param':
            raise DominioError('PARAMETRO_INVENTARIO_INVALIDO', 'Producto sin parametro inventario', 400)
        self.db.commit()
        return {'id_reposicion': r.id_reposicion}