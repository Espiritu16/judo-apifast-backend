from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.deps import get_current_user, get_db
from app.modules.reportes.service import ReporteService as ReporteServ
from app.modules.usuarios.model import Usuario
from app.shared.responses import respuesta_ok
router = APIRouter()
#API que muestra un reporte de valorización
@router.get('/valorizacion')
def reporte_valorizacion(db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    return respuesta_ok('Reporte de valorización generado', ReporteServ(db).reporte_valorizacion())
@router.get('/rotacion')
#API que muestra un reporte de rotación
def reporte_rotacion(db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    return respuesta_ok('Reporte de rotación generado', ReporteServ(db).reporte_rotacion())
#API que muestra un reporte de stock crítico
@router.get('/stock-critico')
def reporte_stock_critico(db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    return respuesta_ok('Reporte de stock crítico generado', ReporteServ(db).reporte_stock_critico())
