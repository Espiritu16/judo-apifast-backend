from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.deps import get_db
from app.core.security import crear_token_acceso
from app.main import app
from app.modules.auditoria.model import AuditoriaEvento
from app.modules.usuarios.model import Usuario


@pytest.fixture(autouse=True)
def clear_dependency_overrides() -> Generator[None]:
    app.dependency_overrides.clear()
    yield
    app.dependency_overrides.clear()


def test_listar_auditoria_responde_200_con_lista_vacia(monkeypatch):
    TestingSessionLocal = _build_testing_db()
    _seed_duena(TestingSessionLocal)
    _override_db(TestingSessionLocal, monkeypatch)

    client = TestClient(app)
    response = client.get(
        "/api/v1/auditoria?limit=100",
        headers={
            "Authorization": f"Bearer {_token_duena()}",
            "Origin": "https://proyectoutp.com",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "https://proyectoutp.com"
    assert response.json() == {
        "ok": True,
        "mensaje": "Eventos de auditoría listados",
        "datos": [],
    }


def test_error_de_auditoria_mantiene_headers_cors(monkeypatch):
    TestingSessionLocal = _build_testing_db()
    _seed_duena(TestingSessionLocal)
    _override_db(TestingSessionLocal, monkeypatch)

    client = TestClient(app)
    response = client.get(
        "/api/v1/auditoria?limit=0",
        headers={
            "Authorization": f"Bearer {_token_duena()}",
            "Origin": "https://proyectoutp.com",
        },
    )

    assert response.status_code == 400
    assert response.headers["access-control-allow-origin"] == "https://proyectoutp.com"
    assert response.json()["codigo"] == "VALIDATION_ERROR"


def _build_testing_db() -> sessionmaker[Session]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Usuario.__table__.create(bind=engine)
    AuditoriaEvento.__table__.create(bind=engine)
    return TestingSessionLocal


def _seed_duena(TestingSessionLocal: sessionmaker[Session]) -> None:
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
