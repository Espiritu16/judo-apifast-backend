from types import SimpleNamespace

import pytest

from app.modules.reposiciones.service import ReposicionesService
from app.shared.exceptions import DominioError


class FakeDb:
    def commit(self):
        raise AssertionError("No debe confirmar cambios")

    def refresh(self, _):
        raise AssertionError("No debe refrescar cambios")


def test_no_permite_marcar_recibida_desde_cambio_estado_generico():
    service = ReposicionesService.__new__(ReposicionesService)
    service.db = FakeDb()
    service.repo = SimpleNamespace(
        get_reposicion=lambda _id: SimpleNamespace(
            id_reposicion=1,
            codigo_reposicion="REP-001",
            estado_reposicion="SOLICITADA",
            fecha_recepcion=None,
        ),
        set_estado=lambda *_args: pytest.fail("No debe cambiar estado a RECIBIDA por PATCH"),
    )

    with pytest.raises(DominioError) as exc:
        service.cambiar_estado(
            1,
            {"nuevo_estado": "RECIBIDA", "observacion": None},
            SimpleNamespace(id_usuario=7),
        )

    assert exc.value.codigo == "TRANSICION_ESTADO_INVALIDA"


def test_recepcion_rechaza_detalles_duplicados_antes_de_sumar_stock():
    service = _service_para_recepcion(
        detalles=[
            SimpleNamespace(id_detalle_reposicion=10, cantidad_solicitada=3, cantidad_recibida=0),
        ]
    )

    with pytest.raises(DominioError) as exc:
        service.recibir_reposicion(
            1,
            {
                "observacion": None,
                "detalles": [
                    {"id_detalle_reposicion": 10, "cantidad_recibida": 3},
                    {"id_detalle_reposicion": 10, "cantidad_recibida": 3},
                ],
            },
            SimpleNamespace(id_usuario=7),
        )

    assert exc.value.codigo == "DETALLE_DUPLICADO"
    assert service.repo.aplicar_llamado is False


def test_recepcion_rechaza_detalle_ya_recibido_antes_de_crear_movimientos():
    service = _service_para_recepcion(
        detalles=[
            SimpleNamespace(id_detalle_reposicion=10, cantidad_solicitada=3, cantidad_recibida=3),
        ]
    )

    with pytest.raises(DominioError) as exc:
        service.recibir_reposicion(
            1,
            {
                "observacion": None,
                "detalles": [{"id_detalle_reposicion": 10, "cantidad_recibida": 3}],
            },
            SimpleNamespace(id_usuario=7),
        )

    assert exc.value.codigo == "DETALLE_YA_RECIBIDO"
    assert service.repo.aplicar_llamado is False


def test_recepcion_rechaza_si_supera_stock_maximo_configurado():
    service = _service_para_recepcion(
        detalles=[
            SimpleNamespace(
                id_detalle_reposicion=10,
                id_producto=99,
                cantidad_solicitada=3,
                cantidad_recibida=0,
                costo_unitario=4,
            ),
        ],
        parametros={
            99: SimpleNamespace(stock_actual=8, stock_maximo=10),
        },
    )

    with pytest.raises(DominioError) as exc:
        service.recibir_reposicion(
            1,
            {
                "observacion": None,
                "detalles": [{"id_detalle_reposicion": 10, "cantidad_recibida": 3}],
            },
            SimpleNamespace(id_usuario=7),
        )

    assert exc.value.codigo == "STOCK_MAXIMO_SUPERADO"
    assert service.repo.aplicar_llamado is False


def test_recepcion_permite_superar_stock_maximo_no_configurado():
    service = _service_para_recepcion(
        detalles=[
            SimpleNamespace(
                id_detalle_reposicion=10,
                id_producto=99,
                cantidad_solicitada=3,
                cantidad_recibida=0,
                costo_unitario=4,
            ),
        ],
        parametros={
            99: SimpleNamespace(stock_actual=8, stock_maximo=0),
        },
        db=FakeDbOk(),
    )

    result = service.recibir_reposicion(
        1,
        {
            "observacion": None,
            "detalles": [{"id_detalle_reposicion": 10, "cantidad_recibida": 3}],
        },
        SimpleNamespace(id_usuario=7),
    )

    assert result["id_reposicion"] == 1
    assert service.repo.aplicar_llamado is True


def test_guardar_reposicion_rechaza_si_pedido_supera_stock_maximo():
    service = _service_para_guardar(
        parametros={
            99: SimpleNamespace(stock_actual=8, stock_maximo=10),
        }
    )

    with pytest.raises(DominioError) as exc:
        service.crear_reposicion(
            {
                "codigo_reposicion": "REP-001",
                "id_proveedor": 1,
                "observacion": None,
                "detalles": [
                    {"id_producto": 99, "cantidad_solicitada": 3, "costo_unitario": 4},
                ],
            },
            SimpleNamespace(id_usuario=7),
        )

    assert exc.value.codigo == "STOCK_MAXIMO_SUPERADO"
    assert service.repo.crear_llamado is False


def _service_para_recepcion(detalles, parametros=None, db=None):
    repo = FakeReposicionesRepo(detalles, parametros or {})
    service = ReposicionesService.__new__(ReposicionesService)
    service.db = db or FakeDb()
    service.repo = repo
    return service


def _service_para_guardar(parametros):
    repo = FakeReposicionesRepo([], parametros)
    service = ReposicionesService.__new__(ReposicionesService)
    service.db = FakeDbRepoGuardar()
    service.repo = repo
    service.proveedor_repo = SimpleNamespace(list_active_category_ids=lambda _id: [3])
    return service


class FakeDbOk:
    def commit(self):
        return None

    def refresh(self, _):
        return None


class FakeReposicionesRepo:
    def __init__(self, detalles, parametros):
        self.detalles = detalles
        self.parametros = parametros
        self.aplicar_llamado = False
        self.crear_llamado = False

    def get_reposicion_for_update(self, _id):
        return SimpleNamespace(
            id_reposicion=1,
            codigo_reposicion="REP-001",
            estado_reposicion="SOLICITADA",
        )

    def has_recepcion_movements(self, _codigo_reposicion):
        return False

    def list_detalles(self, _id):
        return self.detalles

    def list_parametros_by_productos(self, ids_producto):
        return {
            id_producto: self.parametros[id_producto]
            for id_producto in ids_producto
            if id_producto in self.parametros
        }

    def aplicar_recepcion(self, *_args):
        self.aplicar_llamado = True
        return "ok"

    def create_reposicion(self, *_args):
        self.crear_llamado = True
        return SimpleNamespace(id_reposicion=1)

    def get_reposicion(self, _id):
        return SimpleNamespace(
            id_reposicion=1,
            codigo_reposicion="REP-001",
            id_proveedor=1,
            estado_reposicion="RECIBIDA",
            observacion=None,
            fecha_solicitud=None,
            fecha_recepcion=None,
            creado_por=7,
            fecha_creacion=None,
            editado_por=7,
            fecha_edicion=None,
        )


class FakeDbRepoGuardar:
    def get(self, model, _id):
        model_name = getattr(model, "__name__", "")
        if model_name == "Proveedor":
            return SimpleNamespace(estado="ACTIVO")
        if model_name == "Producto":
            return SimpleNamespace(id_categoria=3)
        return None

    def commit(self):
        raise AssertionError("No debe confirmar cambios")

    def refresh(self, _):
        raise AssertionError("No debe refrescar cambios")
