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
  - tipos validos: `ENTRADA`, `SALIDA`, `MERMA`, `AJUSTE_POSITIVO`, `AJUSTE_NEGATIVO`.
  - `ENTRADA` exige `costo_unitario`.
  - `SALIDA`, `MERMA`, `AJUSTE_NEGATIVO` no pueden dejar stock negativo.
- En inventario:
  - `stock_maximo >= stock_minimo`.
  - calculo de sugerida en stock critico segun reglas del modulo.
- En reposiciones:
  - transiciones validas: `BORRADOR -> SOLICITADA/ANULADA`, `SOLICITADA -> RECIBIDA/ANULADA`, `RECIBIDA -> CERRADA`.
  - `ANULADA` y `CERRADA` terminales.
  - al recibir reposicion se generan movimientos `ENTRADA` por detalle.
  - solo `DUEÑA` puede anular/cerrar reposiciones.

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

## 10. Configuracion por entorno
Variables principales en `.env`:

```env
APP_NAME=JUDO API
APP_VERSION=0.1.0
API_PREFIX=/api/v1
DATABASE_URL=mysql+pymysql://root:TU_PASSWORD@localhost:3306/judo_db
JWT_SECRET_KEY=tu_secret
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=120
```

## 11. Ejecucion local
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
uvicorn app.main:app --reload
```

Documentacion interactiva:
- Swagger UI: `http://localhost:8000/docs`
- Healthcheck: `http://localhost:8000/salud`

## 12. Base de datos
- Script MySQL de referencia en: `/Users/sankef/LENGUAJEPROGRAMACION/INFORMES/mySql.sql`
- La tabla `usuario` debe incluir `clave_hash` para login.
