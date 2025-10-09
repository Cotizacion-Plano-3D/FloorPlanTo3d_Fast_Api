from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session
from database import get_db
from services.membresia_service import (
    list_membresias, get_membresia, add_membresia, edit_membresia, remove_membresia
)
from schemas import (
    MembresiaCreate, MembresiaResponse, ErrorResponse, 
    SuccessResponse, DeleteResponse
)
from typing import List

router = APIRouter(
    prefix="/membresias", 
    tags=["Membresías"],
    responses={
        404: {"model": ErrorResponse, "description": "Membresía no encontrada"},
        422: {"model": ErrorResponse, "description": "Error de validación"}
    }
)

@router.get(
    "/",
    response_model=List[MembresiaResponse],
    summary="Listar todas las membresías",
    description="Obtiene una lista de todas las membresías disponibles en el sistema."
)
def get_membresias(db: Session = Depends(get_db)):
    """
    Obtener todas las membresías
    
    Devuelve una lista completa de todas las membresías disponibles, incluyendo:
    - Información básica (nombre, precio, duración)
    - Descripción detallada
    - ID de Stripe si está configurado
    """
    return list_membresias(db)

@router.get(
    "/{membresia_id}",
    response_model=MembresiaResponse,
    summary="Obtener membresía por ID",
    description="Obtiene los detalles de una membresía específica por su ID."
)
def get_membresia_by_id(
    membresia_id: int = Path(..., description="ID único de la membresía", example=1),
    db: Session = Depends(get_db)
):
    """
    Obtener membresía específica
    
    - **membresia_id**: ID único de la membresía a consultar
    
    Devuelve los detalles completos de la membresía solicitada.
    """
    membresia = get_membresia(db, membresia_id)
    if not membresia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Membresía no encontrada"
        )
    return membresia

@router.post(
    "/",
    response_model=MembresiaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nueva membresía",
    description="Crea una nueva membresía en el sistema con los datos proporcionados."
)
def create_membresia(
    membresia: MembresiaCreate,
    db: Session = Depends(get_db)
):
    """
    Crear nueva membresía
    
    - **nombre**: Nombre de la membresía
    - **precio**: Precio en USD (debe ser mayor a 0)
    - **duracion**: Duración en días (debe ser mayor a 0)
    - **descripcion**: Descripción opcional de la membresía
    
    Crea una nueva membresía y la devuelve con su ID asignado.
    """
    return add_membresia(db, membresia.dict())

@router.put(
    "/{membresia_id}",
    response_model=MembresiaResponse,
    summary="Actualizar membresía",
    description="Actualiza los datos de una membresía existente."
)
def update_membresia(
    membresia_id: int = Path(..., description="ID único de la membresía", example=1),
    membresia: MembresiaCreate = ...,
    db: Session = Depends(get_db)
):
    """
    Actualizar membresía existente
    
    - **membresia_id**: ID de la membresía a actualizar
    - **membresia**: Datos nuevos de la membresía
    
    Actualiza todos los campos de la membresía especificada.
    """
    updated = edit_membresia(db, membresia_id, membresia.dict())
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Membresía no encontrada"
        )
    return updated

@router.delete(
    "/{membresia_id}",
    response_model=DeleteResponse,
    summary="Eliminar membresía",
    description="Elimina una membresía del sistema."
)
def delete_membresia(
    membresia_id: int = Path(..., description="ID único de la membresía", example=1),
    db: Session = Depends(get_db)
):
    """
    Eliminar membresía
    
    - **membresia_id**: ID de la membresía a eliminar
    
    Elimina permanentemente la membresía del sistema.
    """
    deleted = remove_membresia(db, membresia_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Membresía no encontrada"
        )
    return DeleteResponse(detail="Membresía eliminada")
