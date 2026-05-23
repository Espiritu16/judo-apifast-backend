from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings


def _build_engine():
    url = make_url(settings.DATABASE_URL)
    query = dict(url.query)

    # JDBC-style params are ignored/unsupported by PyMySQL in this project context.
    query.pop("useSSL", None)
    query.pop("allowPublicKeyRetrieval", None)
    query.pop("serverTimezone", None)

    connect_args = {}
    if url.get_backend_name() == "mysql":
        # Force DB session clock to Peru time for NOW()/CURRENT_TIMESTAMP consistency.
        connect_args["init_command"] = "SET time_zone = '-05:00'"

    normalized_url = url.set(query=query)
    return create_engine(normalized_url, future=True, pool_pre_ping=True, connect_args=connect_args)


engine = _build_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()
