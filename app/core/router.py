from fastapi import APIRouter
from app.modules.autenticacion.router import router as autenticacion_router
from app.modules.categorias.router import router as categorias_router
from app.modules.inventario.router import router as inventario_router
from app.modules.movimientos.router import router as movimientos_router
from app.modules.productos.router import router as productos_router
from app.modules.proveedores.router import router as proveedores_router
from app.modules.reportes.router import router as reportes_router
from app.modules.reposiciones.router import router as reposiciones_router

api_router = APIRouter()
api_router.include_router(autenticacion_router, prefix='/auth', tags=['auth'])
api_router.include_router(categorias_router, prefix='/categorias', tags=['categorias'])
api_router.include_router(productos_router, prefix='/productos', tags=['productos'])
api_router.include_router(proveedores_router, prefix='/proveedores', tags=['proveedores'])
api_router.include_router(inventario_router, prefix='/inventario', tags=['inventario'])
api_router.include_router(movimientos_router, prefix='/movimientos', tags=['movimientos'])
api_router.include_router(reposiciones_router, prefix='/reposiciones', tags=['reposiciones'])
api_router.include_router(reportes_router, prefix='/reportes', tags=['reportes'])
