from app.shared.dates import now_lima_naive

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.inventario.model_movimiento import MovimientoInventario
from app.modules.inventario.model_parametro import ParametroInventario
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
    def get_reposicion_for_update(self, id_reposicion: int) -> Reposicion | None:
        return self.db.execute(
            select(Reposicion)
            .where(Reposicion.id_reposicion == id_reposicion)
            .with_for_update()
        ).scalar_one_or_none()
    def list_detalles(self, id_reposicion: int) -> list[DetalleReposicion]:
        return self.db.execute(select(DetalleReposicion).where(DetalleReposicion.id_reposicion == id_reposicion)).scalars().all()
    def list_detalles_by_reposiciones(self, ids_reposicion: list[int]) -> dict[int, list[DetalleReposicion]]:
        if not ids_reposicion:
            return {}
        detalles = self.db.execute(
            select(DetalleReposicion).where(DetalleReposicion.id_reposicion.in_(ids_reposicion))
        ).scalars().all()
        por_reposicion: dict[int, list[DetalleReposicion]] = {}
        for detalle in detalles:
            por_reposicion.setdefault(detalle.id_reposicion, []).append(detalle)
        return por_reposicion
    def get_detalle(self, id_detalle: int) -> DetalleReposicion | None:
        return self.db.get(DetalleReposicion, id_detalle)
    def list_parametros_by_productos(self, ids_producto: list[int]) -> dict[int, ParametroInventario]:
        if not ids_producto:
            return {}
        parametros = self.db.execute(
            select(ParametroInventario).where(ParametroInventario.id_producto.in_(ids_producto))
        ).scalars().all()
        return {parametro.id_producto: parametro for parametro in parametros}
    def has_recepcion_movements(self, codigo_reposicion: str) -> bool:
        return self.db.execute(
            select(MovimientoInventario.id_movimiento)
            .where(
                MovimientoInventario.referencia == codigo_reposicion,
                MovimientoInventario.tipo_movimiento == 'ENTRADA',
            )
            .limit(1)
        ).first() is not None
    def update_reposicion_borrador(self, repo: Reposicion, data: dict, user_id: int) -> None:
        repo.id_proveedor = data['id_proveedor']
        repo.observacion = data.get('observacion')
        repo.editado_por = user_id
        repo.fecha_edicion = now_lima_naive()

        detalles_actuales = {
            detalle.id_producto: detalle
            for detalle in self.list_detalles(repo.id_reposicion)
        }
        detalles_payload = {
            item['id_producto']: item
            for item in data['detalles']
        }

        for id_producto, detalle in detalles_actuales.items():
            item = detalles_payload.get(id_producto)
            if item is None:
                detalle.cantidad_solicitada = 0
            else:
                detalle.cantidad_solicitada = item['cantidad_solicitada']
                detalle.costo_unitario = item['costo_unitario']
            detalle.editado_por = user_id

        for id_producto, item in detalles_payload.items():
            if id_producto in detalles_actuales:
                continue
            self.db.add(
                DetalleReposicion(
                    id_reposicion=repo.id_reposicion,
                    id_producto=id_producto,
                    cantidad_solicitada=item['cantidad_solicitada'],
                    costo_unitario=item['costo_unitario'],
                    creado_por=user_id,
                )
            )
    def set_estado(self, repo: Reposicion, nuevo_estado: str, observacion: str | None, user_id: int):
        repo.estado_reposicion = nuevo_estado
        repo.observacion = observacion or repo.observacion
        repo.editado_por = user_id
        repo.fecha_edicion = now_lima_naive()
        if nuevo_estado == 'RECIBIDA':
            repo.fecha_recepcion = now_lima_naive()
    def aplicar_recepcion(self, repo: Reposicion, detalles_payload: list[dict], observacion: str | None, user_id: int):
        for item in detalles_payload:
            det = self.get_detalle(item['id_detalle_reposicion'])
            if not det or det.id_reposicion != repo.id_reposicion:
                return None
            det.cantidad_recibida = float(det.cantidad_recibida) + item['cantidad_recibida']
        repo.estado_reposicion = 'RECIBIDA'
        repo.fecha_recepcion = now_lima_naive()
        repo.editado_por = user_id
        repo.fecha_edicion = now_lima_naive()
        return 'ok'
