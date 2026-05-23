"""
Corrección histórica de timestamps a hora Perú (UTC-5).

Estrategia conservadora:
- Solo corrige valores claramente desfasados: timestamp > NOW() + 1 hora.
- Aplica -5 horas.
- Incluye workaround para detalle_reposicion (triggers de UPDATE).
"""

from sqlalchemy import text

from app.core.database import engine


TARGETS = [
    ("categoria", "fecha_creacion"),
    ("categoria", "fecha_edicion"),
    ("categoria", "fecha_inactivacion"),
    ("producto", "fecha_creacion"),
    ("producto", "fecha_edicion"),
    ("producto", "fecha_inactivacion"),
    ("proveedor", "fecha_creacion"),
    ("proveedor", "fecha_edicion"),
    ("proveedor", "fecha_inactivacion"),
    ("proveedor_categoria", "fecha_creacion"),
    ("proveedor_categoria", "fecha_edicion"),
    ("proveedor_categoria", "fecha_inactivacion"),
    ("usuario", "fecha_creacion"),
    ("usuario", "fecha_edicion"),
    ("usuario", "fecha_inactivacion"),
    ("reposicion", "fecha_solicitud"),
    ("reposicion", "fecha_recepcion"),
    ("reposicion", "fecha_creacion"),
    ("reposicion", "fecha_edicion"),
    ("movimiento_inventario", "fecha_movimiento"),
    ("movimiento_inventario", "fecha_creacion"),
    ("movimiento_inventario", "fecha_edicion"),
    ("parametro_inventario", "fecha_creacion"),
    ("parametro_inventario", "fecha_edicion"),
]


def apply_shift(table: str, column: str) -> int:
    with engine.begin() as conn:
        return conn.execute(
            text(
                f"""
                UPDATE {table}
                SET {column} = DATE_SUB({column}, INTERVAL 5 HOUR)
                WHERE {column} IS NOT NULL
                  AND {column} > NOW() + INTERVAL 1 HOUR
                  AND {column} < NOW() + INTERVAL 2 DAY
                """
            )
        ).rowcount


def fix_detalle_with_trigger_workaround() -> tuple[int, int]:
    triggers = ["tg_detalle_reposicion_validar_upd", "tg_detalle_set_edit"]
    original = {}

    with engine.connect() as conn:
        for trg in triggers:
            row = conn.execute(text(f"SHOW CREATE TRIGGER {trg}")).mappings().first()
            original[trg] = row["SQL Original Statement"]

    with engine.begin() as conn:
        for trg in triggers:
            conn.execute(text(f"DROP TRIGGER {trg}"))

    with engine.begin() as conn:
        r1 = conn.execute(
            text(
                """
                UPDATE detalle_reposicion
                SET fecha_creacion = DATE_SUB(fecha_creacion, INTERVAL 5 HOUR)
                WHERE fecha_creacion IS NOT NULL
                  AND fecha_creacion > NOW() + INTERVAL 1 HOUR
                  AND fecha_creacion < NOW() + INTERVAL 2 DAY
                """
            )
        ).rowcount
        r2 = conn.execute(
            text(
                """
                UPDATE detalle_reposicion
                SET fecha_edicion = DATE_SUB(fecha_edicion, INTERVAL 5 HOUR)
                WHERE fecha_edicion IS NOT NULL
                  AND fecha_edicion > NOW() + INTERVAL 1 HOUR
                  AND fecha_edicion < NOW() + INTERVAL 2 DAY
                """
            )
        ).rowcount

    with engine.begin() as conn:
        for trg in triggers:
            conn.execute(text(original[trg]))

    return r1, r2


def main() -> None:
    with engine.connect() as conn:
        now_row = conn.execute(text("SELECT NOW() as now_lima, UTC_TIMESTAMP() as now_utc")).mappings().first()
        print(f"NOW_LIMA={now_row['now_lima']} NOW_UTC={now_row['now_utc']}")

    total = 0
    for table, column in TARGETS:
        rc = apply_shift(table, column)
        if rc:
            total += rc
            print(f"{table}.{column}: {rc} filas corregidas")

    d1, d2 = fix_detalle_with_trigger_workaround()
    if d1:
        total += d1
        print(f"detalle_reposicion.fecha_creacion: {d1} filas corregidas")
    if d2:
        total += d2
        print(f"detalle_reposicion.fecha_edicion: {d2} filas corregidas")

    print(f"TOTAL filas corregidas: {total}")


if __name__ == "__main__":
    main()
