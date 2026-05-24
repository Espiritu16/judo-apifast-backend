# JUDO Backend API

## 1. Descripcion del proyecto
Backend del sistema JUDO para gestion de inventario y logistica de reposicion.

Permite:
- autenticacion y autorizacion por roles,
- gestion de categorias, productos y proveedores,
- control de parametros de inventario y stock,
- registro de movimientos de inventario,
- flujo de reposiciones con transiciones de estado,
- reportes de valorizacion, rotacion y stock critico.

## 2. Objetivo del backend
Centralizar las operaciones de inventario y abastecimiento con reglas de negocio consistentes:

`Catalogos -> Parametrizacion de inventario -> Movimientos -> Reposiciones -> Reportes`

## 3. Arquitectura y stack
| Stack | Descripcion |
|---|---|
| Python 3.11+ | Lenguaje base del backend. |
| FastAPI | Framework para exponer APIs REST y validaciones de entrada/salida. |
| SQLAlchemy 2.x | ORM para acceso a datos y mapeo de entidades. |
| MySQL 8+ | Motor de base de datos relacional principal. |
| Alembic | Gestion de migraciones de esquema. |
| JWT (`python-jose`) | Autenticacion/autorizacion con token Bearer. |
| Passlib | Hash y verificacion de contrasenas. |
| Pydantic Settings | Configuracion por variables de entorno. |

## 4. Dependencias principales
| Dependencia | Uso |
|---|---|
| `fastapi` | API REST y routing. |
| `uvicorn[standard]` | Servidor ASGI para desarrollo/ejecucion. |
| `sqlalchemy` | Persistencia ORM. |
| `alembic` | Migraciones de BD. |
| `pymysql` | Driver MySQL para SQLAlchemy. |
| `python-jose[cryptography]` | Emision/validacion de JWT. |
| `passlib[bcrypt]` | Hash de contrasenas. |
| `pydantic-settings` | Carga de configuracion desde `.env`. |

## 5. Estructura del proyecto
```text
judo-apifast-backend/
├── app/
│   ├── core/                 # Configuracion, seguridad, dependencias, router principal
│   ├── shared/               # Respuestas y excepciones compartidas
│   ├── modules/
│   │   ├── autenticacion/    # Login y usuario autenticado
│   │   ├── categorias/       # CRUD de categorias
│   │   ├── productos/        # CRUD de productos
│   │   ├── proveedores/      # CRUD de proveedores
│   │   ├── inventario/       # Parametros y consultas de stock
│   │   ├── movimientos/      # Registro/listado de movimientos
│   │   ├── reposiciones/     # Flujo de reposicion y recepcion
│   │   ├── reportes/         # Valorizacion, rotacion y stock critico
│   │   └── usuarios/         # Modelo de usuario
│   └── main.py               # Entry point de la API
├── alembic/                  # Configuracion y versiones de migracion
├── tests/                    # Pruebas
├── pyproject.toml
└── README.md
```

## 6. Modulos funcionales
| Modulo | Descripcion |
|---|---|
| `autenticacion` | Login JWT y endpoint `/auth/me`. |
| `categorias` | Alta, consulta, actualizacion e inactivacion de categorias. |
| `productos` | Alta, consulta, actualizacion e inactivacion de productos. |
| `proveedores` | Alta, consulta, actualizacion e inactivacion de proveedores. |
| `inventario` | Consulta de stock, stock critico y parametrizacion por producto. |
| `movimientos` | Registro y consulta de movimientos de inventario. |
| `reposiciones` | Creacion de reposiciones, cambios de estado y recepcion. |
| `reportes` | Reportes de valorizacion, rotacion y stock critico. |

## 7. Reglas de negocio clave
- Roles de usuario permitidos: `DUEÑA`, `EMPLEADO`.
- Estados de catalogo: `ACTIVO` / `INACTIVO`.
- En movimientos:
  - tipos validos: `ENTRADA`, `SALIDA`, `AJUSTE` (con compatibilidad legacy: `MERMA`, `AJUSTE_POSITIVO`, `AJUSTE_NEGATIVO`).
  - `ENTRADA` exige `costo_unitario`.
  - `SALIDA`, `MERMA`, `AJUSTE_NEGATIVO` no pueden dejar stock negativo.
- En inventario:
  - `stock_maximo >= stock_minimo`.
  - calculo de sugerida en stock critico segun reglas del modulo.
- En reposiciones:
  - transiciones validas: `BORRADOR -> SOLICITADA/ANULADA`, `SOLICITADA -> RECIBIDA/ANULADA`, `RECIBIDA -> CERRADA`.
  - `ANULADA` y `CERRADA` terminales.
  - al recibir reposicion se generan movimientos `ENTRADA` por detalle.
  - tanto `DUEÑA` como `EMPLEADO` pueden ejecutar transiciones validas.

## 8. API principal
Base URL: `/api/v1`

| Modulo | Metodo | Endpoint |
|---|---|---|
| Auth | `POST` | `/auth/login` |
| Auth | `GET` | `/auth/me` |
| Categorias | `POST` | `/categorias` |
| Categorias | `GET` | `/categorias` |
| Categorias | `GET` | `/categorias/{id_categoria}` |
| Categorias | `PUT` | `/categorias/{id_categoria}` |
| Categorias | `PATCH` | `/categorias/{id_categoria}/inactivar` |
| Productos | `POST` | `/productos` |
| Productos | `GET` | `/productos` |
| Productos | `GET` | `/productos/{id_producto}` |
| Productos | `PUT` | `/productos/{id_producto}` |
| Productos | `PATCH` | `/productos/{id_producto}/inactivar` |
| Proveedores | `POST` | `/proveedores` |
| Proveedores | `GET` | `/proveedores` |
| Proveedores | `GET` | `/proveedores/{id_proveedor}` |
| Proveedores | `PUT` | `/proveedores/{id_proveedor}` |
| Proveedores | `PATCH` | `/proveedores/{id_proveedor}/inactivar` |
| Inventario | `GET` | `/inventario/stock` |
| Inventario | `GET` | `/inventario/stock/critico` |
| Inventario | `PUT` | `/inventario/parametros/{id_producto}` |
| Movimientos | `POST` | `/movimientos` |
| Movimientos | `GET` | `/movimientos` |
| Movimientos | `GET` | `/movimientos/{id_movimiento}` |
| Reposiciones | `POST` | `/reposiciones` |
| Reposiciones | `GET` | `/reposiciones` |
| Reposiciones | `GET` | `/reposiciones/{id_reposicion}` |
| Reposiciones | `PATCH` | `/reposiciones/{id_reposicion}/estado` |
| Reposiciones | `POST` | `/reposiciones/{id_reposicion}/recibir` |
| Reportes | `GET` | `/reportes/valorizacion` |
| Reportes | `GET` | `/reportes/rotacion` |
| Reportes | `GET` | `/reportes/stock-critico` |

## 9. Seguridad
- Autenticacion con JWT Bearer.
- Endpoint protegido por dependencias de usuario autenticado.
- Control de acceso por rol (`require_roles`).
- Contrasena almacenada hasheada en `usuario.clave_hash`.

## 10. Roles y permisos
| Accion | DUEÑA | EMPLEADO |
|---|---|---|
| Iniciar sesion (`/auth/login`) y ver usuario actual (`/auth/me`) | ✅ | ✅ |
| Registrar movimientos de inventario | ✅ | ✅ |
| Consultar stock y stock critico | ✅ | ✅ |
| Crear reposicion en BORRADOR | ✅ | ✅ |
| Cambiar reposicion a `SOLICITADA` o `RECIBIDA` | ✅ | ✅ |
| Crear categorias | ✅ | ✅ |
| Actualizar/inactivar categorias | ✅ | ✅ |
| Crear productos | ✅ | ✅ |
| Actualizar/inactivar productos | ✅ | ✅ |
| Crear proveedores | ✅ | ✅ |
| Actualizar/inactivar proveedores | ✅ | ✅ |
| Parametrizar inventario (`/inventario/parametros/{id_producto}`) | ✅ | ✅ |
| Cambiar reposicion a `ANULADA` o `CERRADA` | ✅ | ✅ |
| Consultar reportes (`/reportes/*`) | ✅ | ✅ |
| Gestion de usuarios (`/usuarios/*`) | ✅ | ❌ |

## 11. Configuracion por entorno
Variables principales en `.env`:

```env
APP_NAME=JUDO API
APP_VERSION=0.1.0
API_PREFIX=/api/v1
DATABASE_URL=mysql+pymysql://root:TU_PASSWORD@localhost:3306/judo_db
JWT_SECRET_KEY=tu_secret
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=120
FACTILIZA_API_TOKEN=tu_token_factiliza
FACTILIZA_API_BASE_URL=https://api.factiliza.com/v1
FACTILIZA_TIMEOUT_SECONDS=10
```

## 12. Ejecucion local
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
uvicorn app.main:app --reload
```

Documentacion interactiva:
- Swagger UI: `http://localhost:8000/docs`
- Healthcheck: `http://localhost:8000/salud`

## 13. Modelo logico de base de datos (JUDO)
```mermaid
erDiagram
    USUARIO {
        BIGINT id_usuario PK
        VARCHAR correo UK
        VARCHAR nombre_completo
        VARCHAR clave_hash
        ENUM rol "DUEÑA | EMPLEADO"
        ENUM estado "ACTIVO | INACTIVO"
        DATETIME fecha_creacion
        BIGINT creado_por FK
        DATETIME fecha_edicion
        BIGINT editado_por FK
        DATETIME fecha_inactivacion
        BIGINT inactivado_por FK
        VARCHAR motivo_inactivacion
    }

    CATEGORIA {
        BIGINT id_categoria PK
        VARCHAR nombre_categoria UK
        VARCHAR descripcion
        ENUM estado "ACTIVO | INACTIVO"
        DATETIME fecha_creacion
        BIGINT creado_por FK
        DATETIME fecha_edicion
        BIGINT editado_por FK
    }

    PROVEEDOR {
        BIGINT id_proveedor PK
        VARCHAR razon_social
        VARCHAR ruc UK
        VARCHAR telefono
        VARCHAR correo_electronico
        ENUM estado "ACTIVO | INACTIVO"
        DATETIME fecha_creacion
        BIGINT creado_por FK
        DATETIME fecha_edicion
        BIGINT editado_por FK
    }

    PRODUCTO {
        BIGINT id_producto PK
        VARCHAR codigo_producto UK
        VARCHAR nombre_producto
        VARCHAR descripcion
        BIGINT id_categoria FK
        VARCHAR unidad_medida
        DECIMAL costo_unitario_actual
        ENUM estado "ACTIVO | INACTIVO"
        DATETIME fecha_creacion
        BIGINT creado_por FK
        DATETIME fecha_edicion
        BIGINT editado_por FK
    }

    PARAMETRO_INVENTARIO {
        BIGINT id_producto PK,FK
        DECIMAL stock_actual
        DECIMAL stock_minimo
        DECIMAL stock_maximo
        DECIMAL consumo_promedio_diario
        DECIMAL stock_seguridad
        INT tiempo_reposicion_dias
        DECIMAL punto_reorden
        DATETIME fecha_creacion
        BIGINT creado_por FK
        DATETIME fecha_edicion
        BIGINT editado_por FK
    }

    MOVIMIENTO_INVENTARIO {
        BIGINT id_movimiento PK
        BIGINT id_producto FK
        DATETIME fecha_movimiento
        ENUM tipo_movimiento "ENTRADA | SALIDA | MERMA | AJUSTE_POSITIVO | AJUSTE_NEGATIVO"
        DECIMAL cantidad
        DECIMAL costo_unitario
        VARCHAR motivo
        VARCHAR referencia
        VARCHAR observacion
        DATETIME fecha_creacion
        BIGINT creado_por FK
    }

    REPOSICION {
        BIGINT id_reposicion PK
        VARCHAR codigo_reposicion UK
        BIGINT id_proveedor FK
        DATETIME fecha_solicitud
        DATETIME fecha_recepcion
        ENUM estado_reposicion "BORRADOR | SOLICITADA | RECIBIDA | CERRADA | ANULADA"
        VARCHAR observacion
        DATETIME fecha_creacion
        BIGINT creado_por FK
        DATETIME fecha_edicion
        BIGINT editado_por FK
    }

    DETALLE_REPOSICION {
        BIGINT id_detalle_reposicion PK
        BIGINT id_reposicion FK
        BIGINT id_producto FK
        DECIMAL cantidad_solicitada
        DECIMAL cantidad_recibida
        DECIMAL costo_unitario
        DECIMAL subtotal
        DATETIME fecha_creacion
        BIGINT creado_por FK
        DATETIME fecha_edicion
        BIGINT editado_por FK
    }

    CATEGORIA ||--o{ PRODUCTO : "clasifica"
    PRODUCTO ||--|| PARAMETRO_INVENTARIO : "parametriza"
    PRODUCTO ||--o{ MOVIMIENTO_INVENTARIO : "registra"
    PROVEEDOR ||--o{ REPOSICION : "abastece"
    REPOSICION ||--o{ DETALLE_REPOSICION : "detalla"
    PRODUCTO ||--o{ DETALLE_REPOSICION : "incluye"
    USUARIO ||--o{ CATEGORIA : "crea/edita"
    USUARIO ||--o{ PROVEEDOR : "crea/edita"
    USUARIO ||--o{ PRODUCTO : "crea/edita"
    USUARIO ||--o{ MOVIMIENTO_INVENTARIO : "registra"
    USUARIO ||--o{ REPOSICION : "crea/edita"
```

## 14. Diagrama de arquitectura (JUDO)
```mermaid
flowchart TB
  subgraph C1["Capa Cliente"]
    FE["Frontend Angular<br/>Standalone Components + Router"]
  end

  subgraph C2["Capa API (FastAPI)"]
    API["Rutas REST<br/>/auth, /categorias, /productos, /proveedores,<br/>/inventario, /movimientos, /reposiciones, /reportes"]
    SEC["Seguridad<br/>JWT Bearer + RBAC<br/>401/403 respuesta estandar"]
    APP["Servicios de negocio<br/>Reglas logisticas y validaciones"]
  end

  subgraph C3["Capa Persistencia"]
    ORM["SQLAlchemy Repositories"]
    DB[("MySQL judo_db")]
  end

  subgraph M["Modulos de negocio"]
    AUT["Autenticacion<br/>Login + Me"]
    CAT["Categorias<br/>CRUD + Inactivacion"]
    PRO["Productos<br/>CRUD + Parametro inventario"]
    PRV["Proveedores<br/>CRUD + Inactivacion"]
    INV["Inventario<br/>Stock + Critico + Parametros"]
    MOV["Movimientos<br/>Entradas/Salidas/Ajustes/Mermas"]
    REP["Reposiciones<br/>Flujo de estados + Recepcion"]
    RPT["Reportes<br/>Valorizacion + Rotacion + Stock critico"]
  end

  FE -->|"HTTPS JSON"| API
  API --> SEC
  SEC --> APP

  APP --> AUT
  APP --> CAT
  APP --> PRO
  APP --> PRV
  APP --> INV
  APP --> MOV
  APP --> REP
  APP --> RPT

  AUT --> ORM
  CAT --> ORM
  PRO --> ORM
  PRV --> ORM
  INV --> ORM
  MOV --> ORM
  REP --> ORM
  RPT --> ORM
  ORM --> DB
```


## 15. Requerimientos funcionales
| ID | Requerimiento | Descripcion |
|---|---|---|
| RF-01 | Autenticacion de usuarios | El sistema debe permitir iniciar sesion con usuario y contrasena validando `clave_hash` y emitiendo JWT. |
| RF-02 | Consulta de usuario autenticado | El sistema debe exponer `/auth/me` para obtener datos del usuario autenticado. |
| RF-03 | Gestion de categorias | Permitir crear, listar, obtener, actualizar e inactivar categorias. |
| RF-04 | Gestion de productos | Permitir crear, listar, obtener, actualizar e inactivar productos. |
| RF-05 | Gestion de proveedores | Permitir crear, listar, obtener, actualizar e inactivar proveedores. |
| RF-06 | Parametrizacion de inventario | Permitir actualizar parametros por producto (`stock_minimo`, `stock_maximo`, `consumo_promedio_diario`, `stock_seguridad`, `tiempo_reposicion_dias`). |
| RF-07 | Consulta de stock | Permitir consultar stock general y filtrar por nombre de producto. |
| RF-08 | Consulta de stock critico | Permitir listar productos con `stock_actual <= stock_minimo` y mostrar cantidad sugerida. |
| RF-09 | Registro de movimientos | Permitir registrar movimientos de inventario con tipos validos y reglas de negocio. |
| RF-10 | Control de stock negativo | Bloquear salidas/mermas/ajustes negativos que dejen stock menor que cero. |
| RF-11 | Flujo de reposiciones | Permitir crear reposiciones con detalle y gestionar estados `BORRADOR`, `SOLICITADA`, `RECIBIDA`, `CERRADA`, `ANULADA`. |
| RF-12 | Recepcion de reposiciones | Al recibir reposicion, registrar movimientos de entrada por cada detalle y actualizar stock. |
| RF-13 | Reporte de valorizacion | Exponer reporte valorizado por producto y total general. |
| RF-14 | Reporte de rotacion | Exponer rotacion por producto en base a salidas acumuladas y stock actual. |
| RF-15 | Reporte de stock critico | Exponer listado de productos en condicion critica de inventario. |

## 16. Requerimientos no funcionales
| ID | Requerimiento | Descripcion |
|---|---|---|
| RNF-01 | Seguridad de autenticacion | JWT firmado con secreto y algoritmo configurables por entorno. |
| RNF-02 | Control de acceso por roles | Aplicar RBAC en endpoints sensibles con roles `DUEÑA` y `EMPLEADO`. |
| RNF-03 | Seguridad de contrasenas | Almacenar contrasenas hasheadas (`clave_hash`), nunca en texto plano. |
| RNF-04 | Integridad de datos | Usar PK/FK, checks y validaciones de servicio para consistencia de dominio. |
| RNF-05 | Consistencia de errores | Responder errores de negocio con codigos y mensajes estandarizados. |
| RNF-06 | Configuracion por entorno | Gestionar conexion BD, JWT y parametros via variables de entorno. |
| RNF-07 | Mantenibilidad | Mantener arquitectura modular por feature (`autenticacion`, `inventario`, `movimientos`, etc.). |
| RNF-08 | Trazabilidad basica | Registrar campos de auditoria (`creado_por`, `fecha_creacion`, `editado_por`, `fecha_edicion`) en entidades clave. |
| RNF-09 | Compatibilidad API | Mantener prefijo de versionado `/api/v1` para estabilidad de clientes. |
| RNF-10 | Documentacion operativa | Exponer documentacion interactiva en Swagger (`/docs`) para pruebas y consumo de API. |


## 17. Base de datos
- Script MySQL de referencia en: `/Users/sankef/LENGUAJEPROGRAMACION/INFORMES/mySql.sql`
- La tabla `usuario` debe incluir `clave_hash` para login.
