from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from repositories.categoria_repository import CategoriaRepository
from schemas.categoria_schemas import CategoriaCreate, CategoriaUpdate, CategoriaResponse
from schemas.response_schemas import SuccessResponse, ErrorResponse
from models.usuario import Usuario

router = APIRouter(
    prefix="/categorias",
    tags=["Categorías"]
)

@router.post(
    "/",
    response_model=SuccessResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una nueva categoría",
    description="Crea una nueva categoría de materiales"
)
def create_categoria(
    categoria_data: CategoriaCreate,
    db: Session = Depends(get_db),
):
    # Verificar si el código ya existe
    existing = CategoriaRepository.get_by_codigo(db, categoria_data.codigo)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe una categoría con el código '{categoria_data.codigo}'"
        )
    
    categoria = CategoriaRepository.create(db, categoria_data)
    
    return SuccessResponse(
        message="Categoría creada exitosamente",
        data={
            "id": categoria.id,
            "codigo": categoria.codigo,
            "nombre": categoria.nombre,
            "descripcion": categoria.descripcion,
            "imagen_url": categoria.imagen_url,
            "fecha_creacion": categoria.fecha_creacion.isoformat()
        }
    )

@router.get(
    "/",
    response_model=SuccessResponse,
    summary="Listar todas las categorías",
    description="Obtiene todas las categorías con conteo de materiales"
)
def get_categorias(
    db: Session = Depends(get_db)
):
    categorias = CategoriaRepository.get_all_with_count(db, skip=0, limit=None)
    total = CategoriaRepository.count(db)
    
    return SuccessResponse(
        message="Categorías obtenidas exitosamente",
        data={
            "categorias": categorias,
            "total": total
        }
    )

@router.get(
    "/{categoria_id}",
    response_model=SuccessResponse,
    summary="Obtener categoría por ID",
    description="Obtiene los detalles de una categoría específica"
)
def get_categoria(
    categoria_id: int,
    db: Session = Depends(get_db)
):
    categoria = CategoriaRepository.get_by_id(db, categoria_id)
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoría con ID {categoria_id} no encontrada"
        )
    
    return SuccessResponse(
        message="Categoría obtenida exitosamente",
        data={
            "id": categoria.id,
            "codigo": categoria.codigo,
            "nombre": categoria.nombre,
            "descripcion": categoria.descripcion,
            "imagen_url": categoria.imagen_url,
            "fecha_creacion": categoria.fecha_creacion.isoformat(),
            "fecha_actualizacion": categoria.fecha_actualizacion.isoformat()
        }
    )

@router.put(
    "/{categoria_id}",
    response_model=SuccessResponse,
    summary="Actualizar categoría",
    description="Actualiza los datos de una categoría existente"
)
def update_categoria(
    categoria_id: int,
    categoria_data: CategoriaUpdate,
    db: Session = Depends(get_db),
):
    categoria = CategoriaRepository.update(db, categoria_id, categoria_data)
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoría con ID {categoria_id} no encontrada"
        )
    
    return SuccessResponse(
        message="Categoría actualizada exitosamente",
        data={
            "id": categoria.id,
            "codigo": categoria.codigo,
            "nombre": categoria.nombre,
            "descripcion": categoria.descripcion,
            "imagen_url": categoria.imagen_url,
            "fecha_actualizacion": categoria.fecha_actualizacion.isoformat()
        }
    )

@router.delete(
    "/{categoria_id}",
    response_model=SuccessResponse,
    summary="Eliminar categoría",
    description="Elimina una categoría (solo si no tiene materiales asociados)"
)
def delete_categoria(
    categoria_id: int,
    db: Session = Depends(get_db),
):
    # Verificar si la categoría existe
    categoria = CategoriaRepository.get_by_id(db, categoria_id)
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoría con ID {categoria_id} no encontrada"
        )
    
    # Verificar si tiene materiales asociados
    from repositories.material_repository import MaterialRepository
    count_materiales = MaterialRepository.count_by_categoria(db, categoria_id)
    if count_materiales > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se puede eliminar la categoría porque tiene {count_materiales} materiales asociados"
        )
    
    success = CategoriaRepository.delete(db, categoria_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al eliminar la categoría"
        )
    
    return SuccessResponse(
        message="Categoría eliminada exitosamente",
        data={"id": categoria_id}
    )
