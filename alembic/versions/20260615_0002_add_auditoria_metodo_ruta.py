"""add auditoria metodo and ruta columns

Revision ID: 20260615_0002
Revises: None
Create Date: 2026-06-15

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260615_0002"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    _add_column_if_missing("auditoria_evento", sa.Column("metodo", sa.String(length=10), nullable=True))
    _add_column_if_missing("auditoria_evento", sa.Column("ruta", sa.String(length=255), nullable=True))


def downgrade() -> None:
    _drop_column_if_present("auditoria_evento", "ruta")
    _drop_column_if_present("auditoria_evento", "metodo")


def _add_column_if_missing(table_name: str, column: sa.Column) -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if table_name not in inspector.get_table_names():
        return

    existing_columns = {col["name"] for col in inspector.get_columns(table_name)}
    if column.name not in existing_columns:
        op.add_column(table_name, column)


def _drop_column_if_present(table_name: str, column_name: str) -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if table_name not in inspector.get_table_names():
        return

    existing_columns = {col["name"] for col in inspector.get_columns(table_name)}
    if column_name in existing_columns:
        op.drop_column(table_name, column_name)
