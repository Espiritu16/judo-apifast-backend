import importlib.util
from pathlib import Path

from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.modules.auditoria.model import AuditoriaEvento
from app.modules.auditoria.service import AuditoriaService


def test_registrar_evento_persiste_contexto_y_metadata():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine, tables=[AuditoriaEvento.__table__])

    db = TestingSessionLocal()
    try:
        evento = AuditoriaService(db).registrar_evento(
            accion="CREAR_PRODUCTO",
            modulo="productos",
            resultado="EXITO",
            id_usuario=7,
            entidad="producto",
            id_entidad=15,
            ip="127.0.0.1",
            user_agent="pytest",
            metadata={"codigo_producto": "SKU-001"},
        )

        guardado = db.get(AuditoriaEvento, evento.id_auditoria)

        assert guardado is not None
        assert guardado.accion == "CREAR_PRODUCTO"
        assert guardado.modulo == "productos"
        assert guardado.resultado == "EXITO"
        assert guardado.id_usuario == 7
        assert guardado.entidad == "producto"
        assert guardado.id_entidad == 15
        assert guardado.ip == "127.0.0.1"
        assert guardado.user_agent == "pytest"
        assert guardado.extra_metadata == {"codigo_producto": "SKU-001"}
    finally:
        db.close()


def test_listar_eventos_devuelve_lista_vacia_con_tabla_actualizada():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine, tables=[AuditoriaEvento.__table__])

    db = TestingSessionLocal()
    try:
        assert AuditoriaService(db).listar_eventos(limit=100) == []
    finally:
        db.close()


def test_listar_eventos_serializa_metodo_y_ruta():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine, tables=[AuditoriaEvento.__table__])

    db = TestingSessionLocal()
    try:
        AuditoriaService(db).registrar_evento(
            accion="ERROR_DOMINIO",
            modulo="productos",
            resultado="ERROR",
            codigo_error="VALIDATION_ERROR",
            mensaje="Datos inválidos",
            metodo="POST",
            ruta="/api/v1/productos",
        )

        [evento] = AuditoriaService(db).listar_eventos(limit=100)

        assert evento["metodo"] == "POST"
        assert evento["ruta"] == "/api/v1/productos"
    finally:
        db.close()


def test_migracion_agrega_metodo_y_ruta_y_permite_listar_esquema_antiguo():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                CREATE TABLE auditoria_evento (
                  id_auditoria INTEGER PRIMARY KEY AUTOINCREMENT,
                  id_usuario BIGINT NULL,
                  accion VARCHAR(80) NOT NULL,
                  modulo VARCHAR(50) NOT NULL,
                  entidad VARCHAR(80) NULL,
                  id_entidad BIGINT NULL,
                  resultado VARCHAR(20) NOT NULL,
                  codigo_error VARCHAR(80) NULL,
                  mensaje VARCHAR(255) NULL,
                  ip VARCHAR(45) NULL,
                  user_agent VARCHAR(255) NULL,
                  metadata JSON NULL,
                  fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
        )
        migration = _load_auditoria_migration()
        migration.op = Operations(MigrationContext.configure(connection))

        migration.upgrade()
        migration.upgrade()

    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    db = TestingSessionLocal()
    try:
        assert AuditoriaService(db).listar_eventos(limit=100) == []
    finally:
        db.close()


def _load_auditoria_migration():
    path = (
        Path(__file__).resolve().parents[2]
        / "alembic"
        / "versions"
        / "20260615_0002_add_auditoria_metodo_ruta.py"
    )
    spec = importlib.util.spec_from_file_location("add_auditoria_metodo_ruta", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
