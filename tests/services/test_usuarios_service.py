from types import SimpleNamespace

import pytest

from app.core.security import verify_password
from app.modules.usuarios.service import UsuarioService
from app.shared.exceptions import DominioError


def test_actualizar_usuario_cambia_password_si_se_envia():
    user = SimpleNamespace(
        id_usuario=1,
        nombre_completo="Kevin Espiritu",
        correo="kevin@gmail.com",
        rol="EMPLEADO",
        estado="ACTIVO",
        clave_hash="hash-anterior",
        creado_por=1,
        editado_por=None,
        inactivado_por=None,
        fecha_creacion=None,
        fecha_edicion=None,
        fecha_inactivacion=None,
    )
    service = _service(user)

    service.actualizar_usuario(
        1,
        {
            "nombres": "Kevin",
            "apellidos": "Espiritu",
            "correo": "kevin@gmail.com",
            "rol": "EMPLEADO",
            "estado": "ACTIVO",
            "password": "nuevaClave123",
        },
        actor_id=7,
    )

    assert service.repo.updated_data["clave_hash"] != "hash-anterior"
    assert verify_password("nuevaClave123", service.repo.updated_data["clave_hash"])


def test_actualizar_usuario_rechaza_password_corto():
    user = SimpleNamespace(
        id_usuario=1,
        nombre_completo="Kevin Espiritu",
        correo="kevin@gmail.com",
        rol="EMPLEADO",
        estado="ACTIVO",
        clave_hash="hash-anterior",
        creado_por=1,
        editado_por=None,
        inactivado_por=None,
        fecha_creacion=None,
        fecha_edicion=None,
        fecha_inactivacion=None,
    )
    service = _service(user)

    with pytest.raises(DominioError) as exc:
        service.actualizar_usuario(
            1,
            {
                "nombres": "Kevin",
                "apellidos": "Espiritu",
                "correo": "kevin@gmail.com",
                "rol": "EMPLEADO",
                "estado": "ACTIVO",
                "password": "123",
            },
            actor_id=7,
        )

    assert exc.value.codigo == "VALIDATION_ERROR"
    assert service.repo.updated_data is None


def _service(user):
    service = UsuarioService.__new__(UsuarioService)
    service.db = FakeDb()
    service.repo = FakeUsuarioRepo(user)
    return service


class FakeDb:
    def commit(self):
        return None

    def refresh(self, _):
        return None


class FakeUsuarioRepo:
    def __init__(self, user):
        self.user = user
        self.updated_data = None

    def get(self, _id):
        return self.user

    def get_by_email(self, _correo):
        return self.user

    def update(self, user, data, _actor_id):
        self.updated_data = data
        for key, value in data.items():
            setattr(user, key, value)
        return user
