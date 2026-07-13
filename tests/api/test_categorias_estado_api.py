from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.deps import get_db
from app.core.security import crear_token_acceso
from app.main import app
from app.modules.categorias.model import Categoria
from app.modules.usuarios.model import Usuario


@pytest.fixture(autouse=True)
def clear_dependency_overrides() -> Generator[None]:
    app.dependency_overrides.clear()
    yield
    app.dependency_overrides.clear()


def test_activar_categoria_inactiva(monkeypatch):
    TestingSessionLocal = _build_testing_db()
    _seed_data(TestingSessionLocal)
    _override_db(TestingSessionLocal, monkeypatch)

    client = TestClient(app)
    response = client.patch(
        "/api/v1/categorias/1/activar",
        headers={"Authorization": f"Bearer {_token_duena()}"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["mensaje"] == "Categoria activada"
    assert body["datos"]["estado"] == "ACTIVO"
    assert body["datos"]["inactivado_por"] is None
    assert body["datos"]["fecha_inactivacion"] is None


def _build_testing_db() -> sessionmaker[Session]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Usuario.__table__.create(bind=engine)
    Categoria.__table__.create(bind=engine)
    return TestingSessionLocal


def _seed_data(TestingSessionLocal: sessionmaker[Session]) -> None:
    with TestingSessionLocal() as db:
        db.add(
            Usuario(
                id_usuario=1,
                correo="duena@example.com",
                nombre_completo="Dueña Test",
                rol="DUEÑA",
                estado="ACTIVO",
                clave_hash="irrelevant",
            )
        )
        db.add(
            Categoria(
                id_categoria=1,
                nombre_categoria="Lácteos",
                descripcion="Leches y yogures",
                estado="INACTIVO",
                creado_por=1,
                inactivado_por=1,
                motivo_inactivacion="Prueba",
            )
        )
        db.commit()


def _override_db(TestingSessionLocal: sessionmaker[Session], monkeypatch) -> None:
    def override_get_db() -> Generator[Session]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    monkeypatch.setattr("app.main.SessionLocal", TestingSessionLocal)


def _token_duena() -> str:
    return crear_token_acceso({"sub": "1", "rol": "DUEÑA"})
