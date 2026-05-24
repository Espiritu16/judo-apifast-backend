-- Migración segura: habilitar tipo general AJUSTE manteniendo compatibilidad legacy
-- Fecha: 2026-05-24
-- Tabla: movimiento_inventario

START TRANSACTION;

ALTER TABLE movimiento_inventario
  DROP CHECK ck_mov_tipo;

ALTER TABLE movimiento_inventario
  ADD CONSTRAINT ck_mov_tipo
  CHECK (tipo_movimiento IN ('ENTRADA','SALIDA','AJUSTE','MERMA','AJUSTE_POSITIVO','AJUSTE_NEGATIVO'));

COMMIT;
