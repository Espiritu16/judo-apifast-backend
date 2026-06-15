from logging.config import fileConfig

from alembic import context
from sqlalchemy.engine import make_url
from sqlalchemy import engine_from_config, pool

from app.core.config import settings
from app.core.database import Base

# Import models so Alembic can discover metadata
from app.modules.usuarios.model import Usuario  # noqa: F401
from app.modules.auditoria.model import AuditoriaEvento  # noqa: F401
from app.modules.categorias.model import Categoria  # noqa: F401
from app.modules.proveedores.model import Proveedor  # noqa: F401
from app.modules.productos.model import Producto  # noqa: F401
from app.modules.inventario.model_parametro import ParametroInventario  # noqa: F401
from app.modules.inventario.model_movimiento import MovimientoInventario  # noqa: F401
from app.modules.reposiciones.model_reposicion import Reposicion  # noqa: F401
from app.modules.reposiciones.model_detalle import DetalleReposicion  # noqa: F401

config = context.config
database_url = make_url(settings.DATABASE_URL)
query = dict(database_url.query)
query.pop("useSSL", None)
query.pop("allowPublicKeyRetrieval", None)
query.pop("serverTimezone", None)
config.set_main_option("sqlalchemy.url", str(database_url.set(query=query)))

if config.config_file_name is not None:
    try:
        fileConfig(config.config_file_name)
    except KeyError:
        # Allow running with a minimal alembic.ini that doesn't define logging sections.
        pass

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
