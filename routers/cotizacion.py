"""
Router para endpoints de Cotización
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from middleware.auth_middleware import get_current_user
from repositories.cotizacion_repository import CotizacionRepository
from repositories.plano_repository import PlanoRepository
from schemas.cotizacion_schemas import CotizacionCreate, CotizacionResponse, MaterialCotizacion
from schemas.response_schemas import SuccessResponse

router = APIRouter(prefix="/cotizaciones", tags=["cotizaciones"])

@router.post("/", response_model=CotizacionResponse)
async def create_cotizacion(
    cotizacion_data: CotizacionCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Crear una nueva cotización"""
    # Verificar que el plano existe y pertenece al usuario
    plano_repo = PlanoRepository(db)
    plano = plano_repo.get_by_id(cotizacion_data.plano_id, current_user.id)
    
    if not plano:
        raise HTTPException(status_code=404, detail="Plano no encontrado")
    
    # Crear cotización
    cotizacion_repo = CotizacionRepository(db)
    cotizacion = cotizacion_repo.create(cotizacion_data, current_user.id)
    
    # Convertir materiales de JSON a objetos Pydantic
    materiales_parsed = [MaterialCotizacion(**m) for m in cotizacion.materiales]
    
    return CotizacionResponse(
        id=cotizacion.id,
        plano_id=cotizacion.plano_id,
        usuario_id=cotizacion.usuario_id,
        cliente_nombre=cotizacion.cliente_nombre,
        cliente_email=cotizacion.cliente_email,
        cliente_telefono=cotizacion.cliente_telefono,
        descripcion=cotizacion.descripcion,
        materiales=materiales_parsed,
        subtotal=cotizacion.subtotal,
        iva=cotizacion.iva,
        total=cotizacion.total,
        fecha_creacion=cotizacion.fecha_creacion,
        fecha_actualizacion=cotizacion.fecha_actualizacion
    )

@router.get("/plano/{plano_id}", response_model=List[CotizacionResponse])
async def get_cotizaciones_by_plano(
    plano_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Obtener todas las cotizaciones de un plano"""
    # Verificar que el plano existe y pertenece al usuario
    plano_repo = PlanoRepository(db)
    plano = plano_repo.get_by_id(plano_id, current_user.id)
    
    if not plano:
        raise HTTPException(status_code=404, detail="Plano no encontrado")
    
    # Obtener cotizaciones
    cotizacion_repo = CotizacionRepository(db)
    cotizaciones = cotizacion_repo.get_by_plano(plano_id, current_user.id)
    
    # Convertir a response
    result = []
    for cotizacion in cotizaciones:
        materiales_parsed = [MaterialCotizacion(**m) for m in cotizacion.materiales]
        result.append(CotizacionResponse(
            id=cotizacion.id,
            plano_id=cotizacion.plano_id,
            usuario_id=cotizacion.usuario_id,
            cliente_nombre=cotizacion.cliente_nombre,
            cliente_email=cotizacion.cliente_email,
            cliente_telefono=cotizacion.cliente_telefono,
            descripcion=cotizacion.descripcion,
            materiales=materiales_parsed,
            subtotal=cotizacion.subtotal,
            iva=cotizacion.iva,
            total=cotizacion.total,
            fecha_creacion=cotizacion.fecha_creacion,
            fecha_actualizacion=cotizacion.fecha_actualizacion
        ))
    
    return result

@router.get("/{cotizacion_id}", response_model=CotizacionResponse)
async def get_cotizacion(
    cotizacion_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Obtener una cotización específica"""
    cotizacion_repo = CotizacionRepository(db)
    cotizacion = cotizacion_repo.get_by_id(cotizacion_id, current_user.id)
    
    if not cotizacion:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")
    
    materiales_parsed = [MaterialCotizacion(**m) for m in cotizacion.materiales]
    
    return CotizacionResponse(
        id=cotizacion.id,
        plano_id=cotizacion.plano_id,
        usuario_id=cotizacion.usuario_id,
        cliente_nombre=cotizacion.cliente_nombre,
        cliente_email=cotizacion.cliente_email,
        cliente_telefono=cotizacion.cliente_telefono,
        descripcion=cotizacion.descripcion,
        materiales=materiales_parsed,
        subtotal=cotizacion.subtotal,
        iva=cotizacion.iva,
        total=cotizacion.total,
        fecha_creacion=cotizacion.fecha_creacion,
        fecha_actualizacion=cotizacion.fecha_actualizacion
    )

@router.get("/", response_model=List[CotizacionResponse])
async def get_cotizaciones_usuario(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Obtener todas las cotizaciones del usuario"""
    cotizacion_repo = CotizacionRepository(db)
    cotizaciones = cotizacion_repo.get_all_by_usuario(current_user.id, skip, limit)
    
    result = []
    for cotizacion in cotizaciones:
        materiales_parsed = [MaterialCotizacion(**m) for m in cotizacion.materiales]
        result.append(CotizacionResponse(
            id=cotizacion.id,
            plano_id=cotizacion.plano_id,
            usuario_id=cotizacion.usuario_id,
            cliente_nombre=cotizacion.cliente_nombre,
            cliente_email=cotizacion.cliente_email,
            cliente_telefono=cotizacion.cliente_telefono,
            descripcion=cotizacion.descripcion,
            materiales=materiales_parsed,
            subtotal=cotizacion.subtotal,
            iva=cotizacion.iva,
            total=cotizacion.total,
            fecha_creacion=cotizacion.fecha_creacion,
            fecha_actualizacion=cotizacion.fecha_actualizacion
        ))
    
    return result

@router.delete("/{cotizacion_id}", response_model=SuccessResponse)
async def delete_cotizacion(
    cotizacion_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Eliminar una cotización"""
    cotizacion_repo = CotizacionRepository(db)
    success = cotizacion_repo.delete(cotizacion_id, current_user.id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")
    
    return SuccessResponse(message="Cotización eliminada exitosamente")

