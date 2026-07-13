-- MySQL dump 10.13  Distrib 9.5.0, for macos26.1 (arm64)
--
-- Host: viaduct.proxy.rlwy.net    Database: judo_db
-- ------------------------------------------------------
-- Server version	9.4.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `categoria`
--

DROP TABLE IF EXISTS `categoria`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categoria` (
  `id_categoria` bigint NOT NULL AUTO_INCREMENT,
  `nombre_categoria` varchar(80) NOT NULL,
  `descripcion` varchar(255) DEFAULT NULL,
  `estado` varchar(10) NOT NULL DEFAULT 'ACTIVO',
  `fecha_creacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `creado_por` bigint NOT NULL,
  `fecha_edicion` datetime DEFAULT NULL,
  `editado_por` bigint DEFAULT NULL,
  `fecha_inactivacion` datetime DEFAULT NULL,
  `inactivado_por` bigint DEFAULT NULL,
  `motivo_inactivacion` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id_categoria`),
  UNIQUE KEY `nombre_categoria` (`nombre_categoria`),
  KEY `fk_categoria_creado_por` (`creado_por`),
  KEY `fk_categoria_editado_por` (`editado_por`),
  KEY `fk_categoria_inactivado_por` (`inactivado_por`),
  CONSTRAINT `fk_categoria_creado_por` FOREIGN KEY (`creado_por`) REFERENCES `usuario` (`id_usuario`),
  CONSTRAINT `fk_categoria_editado_por` FOREIGN KEY (`editado_por`) REFERENCES `usuario` (`id_usuario`),
  CONSTRAINT `fk_categoria_inactivado_por` FOREIGN KEY (`inactivado_por`) REFERENCES `usuario` (`id_usuario`),
  CONSTRAINT `ck_categoria_estado` CHECK ((`estado` in (_utf8mb4'ACTIVO',_utf8mb4'INACTIVO'))),
  CONSTRAINT `ck_categoria_inactivacion` CHECK ((((`estado` = _utf8mb4'INACTIVO') and (`fecha_inactivacion` is not null) and (`inactivado_por` is not null)) or (`estado` = _utf8mb4'ACTIVO')))
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categoria`
--

LOCK TABLES `categoria` WRITE;
/*!40000 ALTER TABLE `categoria` DISABLE KEYS */;
INSERT INTO `categoria` VALUES (1,'Lácteos','Productos lácteos en general','ACTIVO','2026-05-23 15:38:04',1,NULL,NULL,NULL,NULL,NULL),(2,'Yogures','Yogures bebibles y aflanados','ACTIVO','2026-05-23 15:38:05',1,NULL,NULL,NULL,NULL,NULL),(3,'Quesos','Quesos frescos y maduros','ACTIVO','2026-05-23 15:38:07',1,NULL,NULL,NULL,NULL,NULL);
/*!40000 ALTER TABLE `categoria` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`%`*/ /*!50003 TRIGGER `tg_categoria_set_edit` BEFORE UPDATE ON `categoria` FOR EACH ROW BEGIN
    SET NEW.fecha_edicion = CURRENT_TIMESTAMP;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `detalle_reposicion`
--

DROP TABLE IF EXISTS `detalle_reposicion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `detalle_reposicion` (
  `id_detalle_reposicion` bigint NOT NULL AUTO_INCREMENT,
  `id_reposicion` bigint NOT NULL,
  `id_producto` bigint NOT NULL,
  `cantidad_solicitada` decimal(12,2) NOT NULL,
  `cantidad_recibida` decimal(12,2) NOT NULL DEFAULT '0.00',
  `costo_unitario` decimal(12,2) NOT NULL,
  `subtotal` decimal(14,2) GENERATED ALWAYS AS ((`cantidad_recibida` * `costo_unitario`)) STORED,
  `fecha_creacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `creado_por` bigint NOT NULL,
  `fecha_edicion` datetime DEFAULT NULL,
  `editado_por` bigint DEFAULT NULL,
  PRIMARY KEY (`id_detalle_reposicion`),
  KEY `fk_detalle_reposicion` (`id_reposicion`),
  KEY `fk_detalle_producto` (`id_producto`),
  KEY `fk_detalle_creado_por` (`creado_por`),
  KEY `fk_detalle_editado_por` (`editado_por`),
  CONSTRAINT `fk_detalle_creado_por` FOREIGN KEY (`creado_por`) REFERENCES `usuario` (`id_usuario`),
  CONSTRAINT `fk_detalle_editado_por` FOREIGN KEY (`editado_por`) REFERENCES `usuario` (`id_usuario`),
  CONSTRAINT `fk_detalle_producto` FOREIGN KEY (`id_producto`) REFERENCES `producto` (`id_producto`),
  CONSTRAINT `fk_detalle_reposicion` FOREIGN KEY (`id_reposicion`) REFERENCES `reposicion` (`id_reposicion`),
  CONSTRAINT `ck_det_cant_recibida` CHECK ((`cantidad_recibida` >= 0)),
  CONSTRAINT `ck_det_cant_solicitada` CHECK ((`cantidad_solicitada` > 0)),
  CONSTRAINT `ck_det_costo` CHECK ((`costo_unitario` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `detalle_reposicion`
--

LOCK TABLES `detalle_reposicion` WRITE;
/*!40000 ALTER TABLE `detalle_reposicion` DISABLE KEYS */;
/*!40000 ALTER TABLE `detalle_reposicion` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`%`*/ /*!50003 TRIGGER `tg_detalle_reposicion_validar_ins` BEFORE INSERT ON `detalle_reposicion` FOR EACH ROW BEGIN
    DECLARE v_estado VARCHAR(12);
    DECLARE v_producto_estado VARCHAR(10);

    SELECT estado_reposicion INTO v_estado FROM reposicion WHERE id_reposicion = NEW.id_reposicion;
    IF v_estado IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'REPOSICION_NO_ENCONTRADA';
    END IF;

    IF v_estado NOT IN ('BORRADOR', 'SOLICITADA') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'TRANSICION_ESTADO_INVALIDA: no se puede modificar detalle en este estado';
    END IF;

    SELECT estado INTO v_producto_estado FROM producto WHERE id_producto = NEW.id_producto;
    IF v_producto_estado IS NULL OR v_producto_estado <> 'ACTIVO' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'PRODUCTO_NO_ENCONTRADO: producto inexistente o inactivo';
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`%`*/ /*!50003 TRIGGER `tg_detalle_reposicion_validar_upd` BEFORE UPDATE ON `detalle_reposicion` FOR EACH ROW BEGIN
    DECLARE v_estado VARCHAR(12);
    DECLARE v_producto_estado VARCHAR(10);

    SELECT estado_reposicion INTO v_estado FROM reposicion WHERE id_reposicion = NEW.id_reposicion;
    IF v_estado IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'REPOSICION_NO_ENCONTRADA';
    END IF;

    IF v_estado NOT IN ('BORRADOR', 'SOLICITADA') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'TRANSICION_ESTADO_INVALIDA: no se puede modificar detalle en este estado';
    END IF;

    SELECT estado INTO v_producto_estado FROM producto WHERE id_producto = NEW.id_producto;
    IF v_producto_estado IS NULL OR v_producto_estado <> 'ACTIVO' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'PRODUCTO_NO_ENCONTRADO: producto inexistente o inactivo';
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`%`*/ /*!50003 TRIGGER `tg_detalle_set_edit` BEFORE UPDATE ON `detalle_reposicion` FOR EACH ROW BEGIN
    SET NEW.fecha_edicion = CURRENT_TIMESTAMP;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`%`*/ /*!50003 TRIGGER `tg_detalle_reposicion_no_delete` BEFORE DELETE ON `detalle_reposicion` FOR EACH ROW BEGIN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No se permite eliminacion fisica en detalle_reposicion';
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `movimiento_inventario`
--

DROP TABLE IF EXISTS `movimiento_inventario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `movimiento_inventario` (
  `id_movimiento` bigint NOT NULL AUTO_INCREMENT,
  `id_producto` bigint NOT NULL,
  `fecha_movimiento` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `tipo_movimiento` varchar(20) NOT NULL,
  `cantidad` decimal(12,2) NOT NULL,
  `costo_unitario` decimal(12,2) DEFAULT NULL,
  `motivo` varchar(120) NOT NULL,
  `referencia` varchar(50) DEFAULT NULL,
  `observacion` varchar(255) DEFAULT NULL,
  `fecha_creacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `creado_por` bigint NOT NULL,
  `fecha_edicion` datetime DEFAULT NULL,
  `editado_por` bigint DEFAULT NULL,
  PRIMARY KEY (`id_movimiento`),
  KEY `fk_movimiento_creado_por` (`creado_por`),
  KEY `fk_movimiento_editado_por` (`editado_por`),
  KEY `idx_movimiento_producto_fecha` (`id_producto`,`fecha_movimiento`),
  CONSTRAINT `fk_movimiento_creado_por` FOREIGN KEY (`creado_por`) REFERENCES `usuario` (`id_usuario`),
  CONSTRAINT `fk_movimiento_editado_por` FOREIGN KEY (`editado_por`) REFERENCES `usuario` (`id_usuario`),
  CONSTRAINT `fk_movimiento_producto` FOREIGN KEY (`id_producto`) REFERENCES `producto` (`id_producto`),
  CONSTRAINT `ck_mov_cantidad` CHECK ((`cantidad` > 0)),
  CONSTRAINT `ck_mov_costo` CHECK (((`costo_unitario` is null) or (`costo_unitario` >= 0))),
  CONSTRAINT `ck_mov_costo_entrada` CHECK ((((`tipo_movimiento` = _utf8mb4'ENTRADA') and (`costo_unitario` is not null)) or (`tipo_movimiento` <> _utf8mb4'ENTRADA'))),
  CONSTRAINT `ck_mov_motivo` CHECK ((length(trim(`motivo`)) > 0)),
  CONSTRAINT `ck_mov_tipo` CHECK ((`tipo_movimiento` in (_utf8mb4'ENTRADA',_utf8mb4'SALIDA',_utf8mb4'AJUSTE',_utf8mb4'MERMA',_utf8mb4'AJUSTE_POSITIVO',_utf8mb4'AJUSTE_NEGATIVO')))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `movimiento_inventario`
--

LOCK TABLES `movimiento_inventario` WRITE;
/*!40000 ALTER TABLE `movimiento_inventario` DISABLE KEYS */;
/*!40000 ALTER TABLE `movimiento_inventario` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`%`*/ /*!50003 TRIGGER `tg_movimiento_aplicar_stock` AFTER INSERT ON `movimiento_inventario` FOR EACH ROW BEGIN
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
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`%`*/ /*!50003 TRIGGER `tg_movimiento_set_edit` BEFORE UPDATE ON `movimiento_inventario` FOR EACH ROW BEGIN
    SET NEW.fecha_edicion = CURRENT_TIMESTAMP;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`%`*/ /*!50003 TRIGGER `tg_movimiento_no_delete` BEFORE DELETE ON `movimiento_inventario` FOR EACH ROW BEGIN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No se permite eliminacion fisica en movimiento_inventario';
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `parametro_inventario`
--

DROP TABLE IF EXISTS `parametro_inventario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `parametro_inventario` (
  `id_producto` bigint NOT NULL,
  `stock_actual` decimal(12,2) NOT NULL DEFAULT '0.00',
  `stock_minimo` decimal(12,2) NOT NULL DEFAULT '0.00',
  `stock_maximo` decimal(12,2) NOT NULL DEFAULT '0.00',
  `consumo_promedio_diario` decimal(12,2) NOT NULL DEFAULT '0.00',
  `stock_seguridad` decimal(12,2) NOT NULL DEFAULT '0.00',
  `tiempo_reposicion_dias` int NOT NULL DEFAULT '0',
  `punto_reorden` decimal(12,2) GENERATED ALWAYS AS (((`consumo_promedio_diario` * `tiempo_reposicion_dias`) + `stock_seguridad`)) STORED,
  `fecha_creacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `creado_por` bigint NOT NULL,
  `fecha_edicion` datetime DEFAULT NULL,
  `editado_por` bigint DEFAULT NULL,
  `estado_stock` varchar(15) GENERATED ALWAYS AS ((case when (`stock_actual` <= 0) then _utf8mb4'AGOTADO' when (`stock_actual` <= `stock_minimo`) then _utf8mb4'STOCK_BAJO' else _utf8mb4'DISPONIBLE' end)) STORED,
  PRIMARY KEY (`id_producto`),
  KEY `fk_parametro_creado_por` (`creado_por`),
  KEY `fk_parametro_editado_por` (`editado_por`),
  CONSTRAINT `fk_parametro_creado_por` FOREIGN KEY (`creado_por`) REFERENCES `usuario` (`id_usuario`),
  CONSTRAINT `fk_parametro_editado_por` FOREIGN KEY (`editado_por`) REFERENCES `usuario` (`id_usuario`),
  CONSTRAINT `fk_parametro_producto` FOREIGN KEY (`id_producto`) REFERENCES `producto` (`id_producto`),
  CONSTRAINT `ck_parametro_consumo` CHECK ((`consumo_promedio_diario` >= 0)),
  CONSTRAINT `ck_parametro_min_max` CHECK ((`stock_maximo` >= `stock_minimo`)),
  CONSTRAINT `ck_parametro_seguridad` CHECK ((`stock_seguridad` >= 0)),
  CONSTRAINT `ck_parametro_stock_actual` CHECK ((`stock_actual` >= 0)),
  CONSTRAINT `ck_parametro_stock_maximo` CHECK ((`stock_maximo` >= 0)),
  CONSTRAINT `ck_parametro_stock_minimo` CHECK ((`stock_minimo` >= 0)),
  CONSTRAINT `ck_parametro_tiempo` CHECK ((`tiempo_reposicion_dias` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `parametro_inventario`
--

LOCK TABLES `parametro_inventario` WRITE;
/*!40000 ALTER TABLE `parametro_inventario` DISABLE KEYS */;
INSERT INTO `parametro_inventario` (`id_producto`, `stock_actual`, `stock_minimo`, `stock_maximo`, `consumo_promedio_diario`, `stock_seguridad`, `tiempo_reposicion_dias`, `fecha_creacion`, `creado_por`, `fecha_edicion`, `editado_por`) VALUES (1,0.00,0.00,0.00,0.00,0.00,0,'2026-05-23 15:38:08',1,NULL,NULL),(2,0.00,0.00,0.00,0.00,0.00,0,'2026-05-23 15:38:10',1,NULL,NULL),(3,0.00,0.00,0.00,0.00,0.00,0,'2026-05-23 15:38:11',1,NULL,NULL);
/*!40000 ALTER TABLE `parametro_inventario` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`%`*/ /*!50003 TRIGGER `tg_parametro_set_edit` BEFORE UPDATE ON `parametro_inventario` FOR EACH ROW BEGIN
    SET NEW.fecha_edicion = CURRENT_TIMESTAMP;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `producto`
--

DROP TABLE IF EXISTS `producto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `producto` (
  `id_producto` bigint NOT NULL AUTO_INCREMENT,
  `codigo_producto` varchar(30) NOT NULL,
  `nombre_producto` varchar(120) NOT NULL,
  `descripcion` varchar(255) DEFAULT NULL,
  `id_categoria` bigint NOT NULL,
  `unidad_medida` varchar(20) NOT NULL,
  `costo_unitario_actual` decimal(12,2) NOT NULL,
  `estado` varchar(10) NOT NULL DEFAULT 'ACTIVO',
  `fecha_creacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `creado_por` bigint NOT NULL,
  `fecha_edicion` datetime DEFAULT NULL,
  `editado_por` bigint DEFAULT NULL,
  `fecha_inactivacion` datetime DEFAULT NULL,
  `inactivado_por` bigint DEFAULT NULL,
  `motivo_inactivacion` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id_producto`),
  UNIQUE KEY `codigo_producto` (`codigo_producto`),
  KEY `fk_producto_creado_por` (`creado_por`),
  KEY `fk_producto_editado_por` (`editado_por`),
  KEY `fk_producto_inactivado_por` (`inactivado_por`),
  KEY `idx_producto_nombre` (`nombre_producto`),
  KEY `idx_producto_categoria` (`id_categoria`),
  CONSTRAINT `fk_producto_categoria` FOREIGN KEY (`id_categoria`) REFERENCES `categoria` (`id_categoria`),
  CONSTRAINT `fk_producto_creado_por` FOREIGN KEY (`creado_por`) REFERENCES `usuario` (`id_usuario`),
  CONSTRAINT `fk_producto_editado_por` FOREIGN KEY (`editado_por`) REFERENCES `usuario` (`id_usuario`),
  CONSTRAINT `fk_producto_inactivado_por` FOREIGN KEY (`inactivado_por`) REFERENCES `usuario` (`id_usuario`),
  CONSTRAINT `ck_producto_costo` CHECK ((`costo_unitario_actual` >= 0)),
  CONSTRAINT `ck_producto_estado` CHECK ((`estado` in (_utf8mb4'ACTIVO',_utf8mb4'INACTIVO'))),
  CONSTRAINT `ck_producto_inactivacion` CHECK ((((`estado` = _utf8mb4'INACTIVO') and (`fecha_inactivacion` is not null) and (`inactivado_por` is not null)) or (`estado` = _utf8mb4'ACTIVO')))
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `producto`
--

LOCK TABLES `producto` WRITE;
/*!40000 ALTER TABLE `producto` DISABLE KEYS */;
INSERT INTO `producto` VALUES (1,'GLR-LECH-1L','Leche Evaporada Gloria 1L','Leche evaporada entera',1,'UNIDAD',4.50,'ACTIVO','2026-05-23 15:38:08',1,NULL,NULL,NULL,NULL,NULL),(2,'GLR-YOG-FAM','Yogurt Gloria Fresa 1kg','Yogurt sabor fresa',2,'UNIDAD',7.20,'ACTIVO','2026-05-23 15:38:09',1,NULL,NULL,NULL,NULL,NULL),(3,'GLR-QUES-EDM','Queso Edam Gloria 500g','Queso Edam',3,'UNIDAD',14.90,'ACTIVO','2026-05-23 15:38:11',1,NULL,NULL,NULL,NULL,NULL);
/*!40000 ALTER TABLE `producto` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`%`*/ /*!50003 TRIGGER `tg_producto_validar_relaciones_ins` BEFORE INSERT ON `producto` FOR EACH ROW BEGIN
    DECLARE v_categoria_estado VARCHAR(10);
    SELECT estado INTO v_categoria_estado FROM categoria WHERE id_categoria = NEW.id_categoria;
    IF v_categoria_estado IS NULL OR v_categoria_estado <> 'ACTIVO' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'CATEGORIA_NO_ENCONTRADA: categoria inexistente o inactiva';
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`%`*/ /*!50003 TRIGGER `tg_producto_set_edit` BEFORE UPDATE ON `producto` FOR EACH ROW BEGIN
    SET NEW.fecha_edicion = CURRENT_TIMESTAMP;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`%`*/ /*!50003 TRIGGER `tg_producto_validar_relaciones_upd` BEFORE UPDATE ON `producto` FOR EACH ROW BEGIN
    DECLARE v_categoria_estado VARCHAR(10);
    IF NEW.id_categoria <> OLD.id_categoria THEN
        SELECT estado INTO v_categoria_estado FROM categoria WHERE id_categoria = NEW.id_categoria;
        IF v_categoria_estado IS NULL OR v_categoria_estado <> 'ACTIVO' THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'CATEGORIA_NO_ENCONTRADA: categoria inexistente o inactiva';
        END IF;
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `proveedor`
--

DROP TABLE IF EXISTS `proveedor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `proveedor` (
  `id_proveedor` bigint NOT NULL AUTO_INCREMENT,
  `razon_social` varchar(120) NOT NULL,
  `tipo_documento` varchar(3) NOT NULL DEFAULT 'RUC',
  `numero_documento` varchar(11) NOT NULL,
  `nombre_completo_persona` varchar(180) DEFAULT NULL,
  `ruc` varchar(11) DEFAULT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `correo_electronico` varchar(120) DEFAULT NULL,
  `direccion` varchar(255) DEFAULT NULL,
  `departamento` varchar(80) DEFAULT NULL,
  `provincia` varchar(80) DEFAULT NULL,
  `distrito` varchar(80) DEFAULT NULL,
  `estado_contribuyente` varchar(50) DEFAULT NULL,
  `condicion_contribuyente` varchar(50) DEFAULT NULL,
  `estado` varchar(10) NOT NULL DEFAULT 'ACTIVO',
  `fecha_creacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `creado_por` bigint NOT NULL,
  `fecha_edicion` datetime DEFAULT NULL,
  `editado_por` bigint DEFAULT NULL,
  `fecha_inactivacion` datetime DEFAULT NULL,
  `inactivado_por` bigint DEFAULT NULL,
  `motivo_inactivacion` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id_proveedor`),
  UNIQUE KEY `uq_proveedor_numero_documento` (`numero_documento`),
  UNIQUE KEY `ruc` (`ruc`),
  KEY `fk_proveedor_creado_por` (`creado_por`),
  KEY `fk_proveedor_editado_por` (`editado_por`),
  KEY `fk_proveedor_inactivado_por` (`inactivado_por`),
  CONSTRAINT `fk_proveedor_creado_por` FOREIGN KEY (`creado_por`) REFERENCES `usuario` (`id_usuario`),
  CONSTRAINT `fk_proveedor_editado_por` FOREIGN KEY (`editado_por`) REFERENCES `usuario` (`id_usuario`),
  CONSTRAINT `fk_proveedor_inactivado_por` FOREIGN KEY (`inactivado_por`) REFERENCES `usuario` (`id_usuario`),
  CONSTRAINT `ck_proveedor_estado` CHECK ((`estado` in (_utf8mb4'ACTIVO',_utf8mb4'INACTIVO'))),
  CONSTRAINT `ck_proveedor_inactivacion` CHECK ((((`estado` = _utf8mb4'INACTIVO') and (`fecha_inactivacion` is not null) and (`inactivado_por` is not null)) or (`estado` = _utf8mb4'ACTIVO'))),
  CONSTRAINT `ck_proveedor_numero_documento` CHECK ((((`tipo_documento` = _utf8mb4'DNI') and (char_length(`numero_documento`) = 8)) or ((`tipo_documento` = _utf8mb4'RUC') and (char_length(`numero_documento`) = 11)))),
  CONSTRAINT `ck_proveedor_tipo_documento` CHECK ((`tipo_documento` in (_utf8mb4'DNI',_utf8mb4'RUC')))
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `proveedor`
--

LOCK TABLES `proveedor` WRITE;
/*!40000 ALTER TABLE `proveedor` DISABLE KEYS */;
INSERT INTO `proveedor` VALUES (1,'GLORIA S.A.','RUC','20100190797',NULL,'20100190797','014700000','contacto@gloria.com.pe','Av. República de Panamá 2461','LIMA','LIMA','LA VICTORIA','ACTIVO','HABIDO','ACTIVO','2026-05-23 15:38:12',1,NULL,NULL,NULL,NULL,NULL);
/*!40000 ALTER TABLE `proveedor` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`%`*/ /*!50003 TRIGGER `tg_proveedor_set_edit` BEFORE UPDATE ON `proveedor` FOR EACH ROW BEGIN
    SET NEW.fecha_edicion = CURRENT_TIMESTAMP;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `proveedor_categoria`
--

DROP TABLE IF EXISTS `proveedor_categoria`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `proveedor_categoria` (
  `id_proveedor_categoria` bigint NOT NULL AUTO_INCREMENT,
  `id_proveedor` bigint NOT NULL,
  `id_categoria` bigint NOT NULL,
  `activo` tinyint(1) NOT NULL DEFAULT '1',
  `fecha_creacion` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `creado_por` bigint DEFAULT NULL,
  `fecha_edicion` timestamp NULL DEFAULT NULL,
  `editado_por` bigint DEFAULT NULL,
  `fecha_inactivacion` timestamp NULL DEFAULT NULL,
  `inactivado_por` bigint DEFAULT NULL,
  `motivo_inactivacion` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id_proveedor_categoria`),
  UNIQUE KEY `uq_proveedor_categoria` (`id_proveedor`,`id_categoria`),
  KEY `fk_proveedor_categoria_creado_por` (`creado_por`),
  KEY `fk_proveedor_categoria_editado_por` (`editado_por`),
  KEY `fk_proveedor_categoria_inactivado_por` (`inactivado_por`),
  KEY `idx_pc_proveedor` (`id_proveedor`),
  KEY `idx_pc_categoria` (`id_categoria`),
  KEY `idx_pc_activo` (`activo`),
  CONSTRAINT `fk_proveedor_categoria_categoria` FOREIGN KEY (`id_categoria`) REFERENCES `categoria` (`id_categoria`),
  CONSTRAINT `fk_proveedor_categoria_creado_por` FOREIGN KEY (`creado_por`) REFERENCES `usuario` (`id_usuario`),
  CONSTRAINT `fk_proveedor_categoria_editado_por` FOREIGN KEY (`editado_por`) REFERENCES `usuario` (`id_usuario`),
  CONSTRAINT `fk_proveedor_categoria_inactivado_por` FOREIGN KEY (`inactivado_por`) REFERENCES `usuario` (`id_usuario`),
  CONSTRAINT `fk_proveedor_categoria_proveedor` FOREIGN KEY (`id_proveedor`) REFERENCES `proveedor` (`id_proveedor`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `proveedor_categoria`
--

LOCK TABLES `proveedor_categoria` WRITE;
/*!40000 ALTER TABLE `proveedor_categoria` DISABLE KEYS */;
INSERT INTO `proveedor_categoria` VALUES (1,1,1,1,'2026-05-23 20:38:13',1,NULL,NULL,NULL,NULL,NULL),(2,1,2,1,'2026-05-23 20:38:13',1,NULL,NULL,NULL,NULL,NULL),(3,1,3,1,'2026-05-23 20:38:13',1,NULL,NULL,NULL,NULL,NULL);
/*!40000 ALTER TABLE `proveedor_categoria` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `reposicion`
--

DROP TABLE IF EXISTS `reposicion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `reposicion` (
  `id_reposicion` bigint NOT NULL AUTO_INCREMENT,
  `codigo_reposicion` varchar(30) NOT NULL,
  `id_proveedor` bigint NOT NULL,
  `fecha_solicitud` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_recepcion` datetime DEFAULT NULL,
  `estado_reposicion` varchar(12) NOT NULL DEFAULT 'BORRADOR',
  `observacion` varchar(255) DEFAULT NULL,
  `fecha_creacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `creado_por` bigint NOT NULL,
  `fecha_edicion` datetime DEFAULT NULL,
  `editado_por` bigint DEFAULT NULL,
  PRIMARY KEY (`id_reposicion`),
  UNIQUE KEY `codigo_reposicion` (`codigo_reposicion`),
  KEY `fk_reposicion_creado_por` (`creado_por`),
  KEY `fk_reposicion_editado_por` (`editado_por`),
  KEY `idx_reposicion_proveedor_fecha` (`id_proveedor`,`fecha_solicitud`),
  CONSTRAINT `fk_reposicion_creado_por` FOREIGN KEY (`creado_por`) REFERENCES `usuario` (`id_usuario`),
  CONSTRAINT `fk_reposicion_editado_por` FOREIGN KEY (`editado_por`) REFERENCES `usuario` (`id_usuario`),
  CONSTRAINT `fk_reposicion_proveedor` FOREIGN KEY (`id_proveedor`) REFERENCES `proveedor` (`id_proveedor`),
  CONSTRAINT `ck_rep_cerrada_recepcion` CHECK (((`estado_reposicion` <> _utf8mb4'CERRADA') or (`fecha_recepcion` is not null))),
  CONSTRAINT `ck_rep_estado` CHECK ((`estado_reposicion` in (_utf8mb4'BORRADOR',_utf8mb4'SOLICITADA',_utf8mb4'RECIBIDA',_utf8mb4'CERRADA',_utf8mb4'ANULADA')))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reposicion`
--

LOCK TABLES `reposicion` WRITE;
/*!40000 ALTER TABLE `reposicion` DISABLE KEYS */;
/*!40000 ALTER TABLE `reposicion` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`%`*/ /*!50003 TRIGGER `tg_reposicion_validar_relaciones_ins` BEFORE INSERT ON `reposicion` FOR EACH ROW BEGIN
    DECLARE v_proveedor_estado VARCHAR(10);
    SELECT estado INTO v_proveedor_estado FROM proveedor WHERE id_proveedor = NEW.id_proveedor;
    IF v_proveedor_estado IS NULL OR v_proveedor_estado <> 'ACTIVO' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'PROVEEDOR_NO_ENCONTRADO: proveedor inexistente o inactivo';
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`%`*/ /*!50003 TRIGGER `tg_reposicion_set_edit` BEFORE UPDATE ON `reposicion` FOR EACH ROW BEGIN
    SET NEW.fecha_edicion = CURRENT_TIMESTAMP;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`%`*/ /*!50003 TRIGGER `tg_reposicion_validar_relaciones_upd` BEFORE UPDATE ON `reposicion` FOR EACH ROW BEGIN
    DECLARE v_proveedor_estado VARCHAR(10);
    IF NEW.id_proveedor <> OLD.id_proveedor THEN
        SELECT estado INTO v_proveedor_estado FROM proveedor WHERE id_proveedor = NEW.id_proveedor;
        IF v_proveedor_estado IS NULL OR v_proveedor_estado <> 'ACTIVO' THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'PROVEEDOR_NO_ENCONTRADO: proveedor inexistente o inactivo';
        END IF;
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`%`*/ /*!50003 TRIGGER `tg_reposicion_validar_estado` BEFORE UPDATE ON `reposicion` FOR EACH ROW BEGIN
    DECLARE v_detalles INT DEFAULT 0;

    IF NEW.estado_reposicion <> OLD.estado_reposicion THEN
        IF OLD.estado_reposicion IN ('CERRADA', 'ANULADA') THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'TRANSICION_ESTADO_INVALIDA: estado terminal';
        END IF;

        IF OLD.estado_reposicion = 'BORRADOR' AND NEW.estado_reposicion NOT IN ('SOLICITADA', 'ANULADA') THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'TRANSICION_ESTADO_INVALIDA: BORRADOR';
        ELSEIF OLD.estado_reposicion = 'SOLICITADA' AND NEW.estado_reposicion NOT IN ('RECIBIDA', 'ANULADA') THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'TRANSICION_ESTADO_INVALIDA: SOLICITADA';
        ELSEIF OLD.estado_reposicion = 'RECIBIDA' AND NEW.estado_reposicion <> 'CERRADA' THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'TRANSICION_ESTADO_INVALIDA: RECIBIDA';
        END IF;

        IF NEW.estado_reposicion IN ('SOLICITADA', 'RECIBIDA') THEN
            SELECT COUNT(*) INTO v_detalles FROM detalle_reposicion WHERE id_reposicion = NEW.id_reposicion;
            IF v_detalles = 0 THEN
                SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'REPOSICION_SIN_DETALLE';
            END IF;
        END IF;
    END IF;

    IF NEW.estado_reposicion = 'RECIBIDA' AND NEW.fecha_recepcion IS NULL THEN
        SET NEW.fecha_recepcion = CURRENT_TIMESTAMP;
    END IF;

    IF NEW.estado_reposicion = 'CERRADA' AND NEW.fecha_recepcion IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'TRANSICION_ESTADO_INVALIDA: cerrar sin fecha_recepcion';
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`%`*/ /*!50003 TRIGGER `tg_reposicion_generar_movimientos` AFTER UPDATE ON `reposicion` FOR EACH ROW BEGIN
    IF OLD.estado_reposicion <> 'RECIBIDA' AND NEW.estado_reposicion = 'RECIBIDA' THEN
        INSERT INTO movimiento_inventario (
            id_producto,
            fecha_movimiento,
            tipo_movimiento,
            cantidad,
            costo_unitario,
            motivo,
            referencia,
            observacion,
            creado_por
        )
        SELECT
            dr.id_producto,
            COALESCE(NEW.fecha_recepcion, CURRENT_TIMESTAMP),
            'ENTRADA',
            CASE WHEN dr.cantidad_recibida > 0 THEN dr.cantidad_recibida ELSE dr.cantidad_solicitada END,
            dr.costo_unitario,
            'Recepcion de reposicion',
            NEW.codigo_reposicion,
            'Generado automaticamente al recibir reposicion',
            COALESCE(NEW.editado_por, NEW.creado_por)
        FROM detalle_reposicion dr
        WHERE dr.id_reposicion = NEW.id_reposicion;
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`%`*/ /*!50003 TRIGGER `tg_reposicion_no_delete` BEFORE DELETE ON `reposicion` FOR EACH ROW BEGIN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No se permite eliminacion fisica en reposicion';
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `usuario`
--

DROP TABLE IF EXISTS `usuario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuario` (
  `id_usuario` bigint NOT NULL AUTO_INCREMENT,
  `correo` varchar(120) NOT NULL,
  `nombre_completo` varchar(120) NOT NULL,
  `rol` varchar(30) NOT NULL,
  `estado` varchar(10) NOT NULL DEFAULT 'ACTIVO',
  `clave_hash` varchar(255) NOT NULL DEFAULT '',
  `fecha_creacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `creado_por` bigint DEFAULT NULL,
  `fecha_edicion` datetime DEFAULT NULL,
  `editado_por` bigint DEFAULT NULL,
  `fecha_inactivacion` datetime DEFAULT NULL,
  `inactivado_por` bigint DEFAULT NULL,
  `motivo_inactivacion` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id_usuario`),
  UNIQUE KEY `nombre_usuario` (`correo`),
  CONSTRAINT `ck_usuario_estado` CHECK ((`estado` in (_utf8mb4'ACTIVO',_utf8mb4'INACTIVO'))),
  CONSTRAINT `ck_usuario_inactivacion` CHECK ((((`estado` = _utf8mb4'INACTIVO') and (`fecha_inactivacion` is not null) and (`inactivado_por` is not null)) or (`estado` = _utf8mb4'ACTIVO'))),
  CONSTRAINT `ck_usuario_rol` CHECK ((`rol` in (_utf8mb4'DUENA',_utf8mb4'EMPLEADO')))
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuario`
--

LOCK TABLES `usuario` WRITE;
/*!40000 ALTER TABLE `usuario` DISABLE KEYS */;
INSERT INTO `usuario` VALUES (1,'kevin@gmail.com','Kevin Octavio Espiritu Castillo','DUEÑA','ACTIVO','$pbkdf2-sha256$29000$IyREKGUsBYDQmjMmpLQ25g$TGf/Ms.Wz1WWYSIL6o9TWKpfaFL92B7xA.31HsXIrOw','2026-05-23 04:52:59',NULL,'2026-05-23 05:32:11',NULL,NULL,NULL,NULL),(2,'kevin2@gmail.com','kevin castillo','EMPLEADO','ACTIVO','$pbkdf2-sha256$29000$hVAqJYQwZkyJce4dI.R8Lw$rNvYL/wqSdo8gNc30uZA4kwXR7R0cyLsqmS5FYYSX.w','2026-05-24 09:35:49',1,NULL,NULL,NULL,NULL,NULL);
/*!40000 ALTER TABLE `usuario` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`%`*/ /*!50003 TRIGGER `tg_usuario_set_edit` BEFORE UPDATE ON `usuario` FOR EACH ROW BEGIN
    SET NEW.fecha_edicion = CURRENT_TIMESTAMP;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Dumping events for database 'judo_db'
--

--
-- Dumping routines for database 'judo_db'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-05-27 14:00:38
