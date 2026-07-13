from types import SimpleNamespace

import pytest

from app.modules.inventario.model_movimiento import MovimientoInventario
from app.modules.inventario.model_parametro import ParametroInventario
from app.modules.movimientos.service import MovimientoService
from app.modules.productos.model import Producto
from app.shared.exceptions import DominioError


def test_ajuste_incremento_rechaza_si_supera_stock_maximo():
    parametro = SimpleNamespace(stock_actual=8, stock_maximo=10, stock_seguridad=0)
    db = FakeDb(parametro=parametro)
    service = MovimientoService.__new__(MovimientoService)
    service.db = db

    with pytest.raises(DominioError) as exc:
        service.registrar_movimiento(
            {
                "id_producto": 99,
                "tipo_movimiento": "AJUSTE",
                "cantidad": 3,
                "motivo": "INCREMENTO_AJUSTE",
                "observacion": None,
            },
            SimpleNamespace(id_usuario=7),
        )

    assert exc.value.codigo == "STOCK_MAXIMO_SUPERADO"
    assert db.added == []


def test_ajuste_incremento_no_modifica_stock_en_servicio_y_deja_movimiento_para_trigger():
    parametro = SimpleNamespace(stock_actual=8, stock_maximo=20, stock_seguridad=0)
    db = FakeDb(parametro=parametro)
    service = MovimientoService.__new__(MovimientoService)
    service.db = db

    movimiento = service.registrar_movimiento(
        {
            "id_producto": 99,
            "tipo_movimiento": "AJUSTE",
            "cantidad": 3,
            "motivo": "INCREMENTO_AJUSTE",
            "observacion": "Conteo real superior",
        },
        SimpleNamespace(id_usuario=7),
    )

    assert parametro.stock_actual == 8
    assert movimiento in db.added
    assert movimiento.tipo_movimiento == "AJUSTE"
    assert movimiento.motivo == "INCREMENTO_AJUSTE"
    assert db.committed is True


def test_ajuste_incremento_ignora_stock_maximo_no_configurado():
    parametro = SimpleNamespace(stock_actual=8, stock_maximo=0, stock_seguridad=0)
    db = FakeDb(parametro=parametro)
    service = MovimientoService.__new__(MovimientoService)
    service.db = db

    movimiento = service.registrar_movimiento(
        {
            "id_producto": 99,
            "tipo_movimiento": "AJUSTE",
            "cantidad": 300,
            "motivo": "INCREMENTO_AJUSTE",
            "observacion": None,
        },
        SimpleNamespace(id_usuario=7),
    )

    assert parametro.stock_actual == 8
    assert movimiento in db.added


class FakeDb:
    def __init__(self, parametro):
        self.producto = SimpleNamespace(estado="ACTIVO", costo_unitario_actual=100)
        self.parametro = parametro
        self.added = []
        self.committed = False

    def get(self, model, _id):
        if model is Producto:
            return self.producto
        if model is ParametroInventario:
            return self.parametro
        return None

    def add(self, item):
        self.added.append(item)

    def flush(self):
        return None

    def commit(self):
        self.committed = True

    def rollback(self):
        return None

    def refresh(self, item):
        if isinstance(item, MovimientoInventario):
            item.id_movimiento = 1
