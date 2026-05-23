from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.inventario.model_movimiento import MovimientoInventario
from app.modules.inventario.model_parametro import ParametroInventario
from app.modules.productos.model import Producto
from app.modules.reposiciones.model_detalle import DetalleReposicion
from app.modules.reposiciones.model_reposicion import Reposicion
"Clase repositorio que contendrá funciones que se utilizan en Service de reposiciones"
class ReposicionesRepository:
    def __init__(self,db:Session):
        self.db=db
    def create_reposicion(self, data: dict, user_id: int) -> Reposicion:
        repo = Reposicion(
            codigo_reposicion=data['codigo_reposicion'],
            id_proveedor=data['id_proveedor'],
            estado_reposicion='BORRADOR',
            observacion=data.get('observacion'),
            creado_por=user_id,
        )
        self.db.add(repo)
        self.db.flush()
        for d in data['detalles']:
            self.db.add(
                DetalleReposicion(
                    id_reposicion=repo.id_reposicion,
                    id_producto=d['id_producto'],
                    cantidad_solicitada=d['cantidad_solicitada'],
                    costo_unitario=d['costo_unitario'],
                    creado_por=user_id,
                )
            )
        return repo
    def list_reposiciones(self) -> list[Reposicion]:
        return self.db.execute(select(Reposicion).order_by(Reposicion.id_reposicion.desc())).scalars().all()
    def get_reposicion(self, id_reposicion: int) -> Reposicion | None:
        return self.db.get(Reposicion, id_reposicion)
    def list_detalles(self, id_reposicion: int) -> list[DetalleReposicion]:
        return self.db.execute(select(DetalleReposicion).where(DetalleReposicion.id_reposicion == id_reposicion)).scalars().all()
    def get_detalle(self, id_detalle: int) -> DetalleReposicion | None:
        return self.db.get(DetalleReposicion, id_detalle)
    def set_estado(self, repo: Reposicion, nuevo_estado: str, observacion: str | None, user_id: int):
        repo.estado_reposicion = nuevo_estado
        repo.observacion = observacion or repo.observacion
        repo.editado_por = user_id
        repo.fecha_edicion = datetime.utcnow()
        if nuevo_estado == 'RECIBIDA':
            repo.fecha_recepcion = datetime.utcnow()
    def aplicar_recepcion(self, repo: Reposicion, detalles_payload: list[dict], observacion: str | None, user_id: int):
        for item in detalles_payload:
            det = self.get_detalle(item['id_detalle_reposicion'])
            if not det or det.id_reposicion != repo.id_reposicion:
                return None
            det.cantidad_recibida = float(det.cantidad_recibida) + item['cantidad_recibida']

            pi = self.db.get(ParametroInventario, det.id_producto)
            if not pi:
                return 'missing_param'
            pi.stock_actual = float(pi.stock_actual) + item['cantidad_recibida']

            prod = self.db.get(Producto, det.id_producto)
            prod.costo_unitario_actual = float(det.costo_unitario or prod.costo_unitario_actual)
            self.db.add(
                MovimientoInventario(
                    id_producto=det.id_producto,
                    tipo_movimiento='ENTRADA',
                    cantidad=item['cantidad_recibida'],
                    costo_unitario=float(det.costo_unitario or prod.costo_unitario_actual),
                    motivo='Recepcion de reposicion',
                    referencia=repo.codigo_reposicion,
                    observacion=observacion,
                    creado_por=user_id,
                )
            )
        repo.estado_reposicion = 'RECIBIDA'
        repo.fecha_recepcion = datetime.utcnow()
        repo.editado_por = user_id
        repo.fecha_edicion = datetime.utcnow()
        return 'ok'
