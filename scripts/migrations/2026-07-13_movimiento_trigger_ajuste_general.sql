DROP TRIGGER IF EXISTS tg_movimiento_aplicar_stock;

DELIMITER ;;
CREATE TRIGGER tg_movimiento_aplicar_stock
AFTER INSERT ON movimiento_inventario
FOR EACH ROW
BEGIN
    DECLARE v_stock_actual DECIMAL(12,2);
    DECLARE v_stock_nuevo DECIMAL(12,2);
    DECLARE v_producto_estado VARCHAR(10);

    SELECT estado INTO v_producto_estado FROM producto WHERE id_producto = NEW.id_producto;
    IF v_producto_estado IS NULL OR v_producto_estado <> 'ACTIVO' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'PRODUCTO_NO_ENCONTRADO: producto inexistente o inactivo';
    END IF;

    SELECT stock_actual INTO v_stock_actual
    FROM parametro_inventario
    WHERE id_producto = NEW.id_producto
    FOR UPDATE;

    IF v_stock_actual IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'PARAMETRO_INVENTARIO_INVALIDO: producto sin parametro inventario';
    END IF;

    IF NEW.tipo_movimiento IN ('ENTRADA', 'AJUSTE_POSITIVO')
       OR (NEW.tipo_movimiento = 'AJUSTE' AND NEW.motivo = 'INCREMENTO_AJUSTE') THEN
        SET v_stock_nuevo = v_stock_actual + NEW.cantidad;
    ELSE
        SET v_stock_nuevo = v_stock_actual - NEW.cantidad;
    END IF;

    IF v_stock_nuevo < 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'STOCK_INSUFICIENTE';
    END IF;

    UPDATE parametro_inventario
       SET stock_actual = v_stock_nuevo
     WHERE id_producto = NEW.id_producto;

    IF NEW.tipo_movimiento = 'ENTRADA' AND NEW.costo_unitario IS NOT NULL THEN
        UPDATE producto
           SET costo_unitario_actual = NEW.costo_unitario
         WHERE id_producto = NEW.id_producto;
    END IF;
END ;;
DELIMITER ;
