-- Migración: relación Proveedor <-> Categoría
-- Fecha: 2026-05-23
-- Motor: MySQL 8+

START TRANSACTION;

CREATE TABLE IF NOT EXISTS proveedor_categoria (
  id_proveedor_categoria BIGINT NOT NULL AUTO_INCREMENT,
  id_proveedor BIGINT NOT NULL,
  id_categoria BIGINT NOT NULL,
  activo TINYINT(1) NOT NULL DEFAULT 1,

  fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  creado_por BIGINT NULL,
  fecha_edicion TIMESTAMP NULL DEFAULT NULL,
  editado_por BIGINT NULL,
  fecha_inactivacion TIMESTAMP NULL DEFAULT NULL,
  inactivado_por BIGINT NULL,
  motivo_inactivacion VARCHAR(255) NULL,

  PRIMARY KEY (id_proveedor_categoria),

  CONSTRAINT uq_proveedor_categoria UNIQUE (id_proveedor, id_categoria),

  CONSTRAINT fk_proveedor_categoria_proveedor
    FOREIGN KEY (id_proveedor) REFERENCES proveedor(id_proveedor),

  CONSTRAINT fk_proveedor_categoria_categoria
    FOREIGN KEY (id_categoria) REFERENCES categoria(id_categoria),

  CONSTRAINT fk_proveedor_categoria_creado_por
    FOREIGN KEY (creado_por) REFERENCES usuario(id_usuario),

  CONSTRAINT fk_proveedor_categoria_editado_por
    FOREIGN KEY (editado_por) REFERENCES usuario(id_usuario),

  CONSTRAINT fk_proveedor_categoria_inactivado_por
    FOREIGN KEY (inactivado_por) REFERENCES usuario(id_usuario)
) ENGINE=InnoDB;

CREATE INDEX idx_pc_proveedor ON proveedor_categoria(id_proveedor);
CREATE INDEX idx_pc_categoria ON proveedor_categoria(id_categoria);
CREATE INDEX idx_pc_activo ON proveedor_categoria(activo);

COMMIT;

-- ROLLBACK (manual):
-- DROP TABLE IF EXISTS proveedor_categoria;
