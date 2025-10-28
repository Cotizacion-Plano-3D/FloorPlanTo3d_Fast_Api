from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from repositories.material_repository import MaterialRepository
from repositories.categoria_repository import CategoriaRepository
from schemas.material_schemas import MaterialCreate, MaterialUpdate, MaterialResponse, MaterialConCategoria
from schemas.response_schemas import SuccessResponse, ErrorResponse
from middleware.auth_middleware import get_current_user
from models.usuario import Usuario

router = APIRouter(
    prefix="/materiales",
    tags=["Materiales"]
)

@router.post(
    "/",
    response_model=SuccessResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo material",
    description="Crea un nuevo material asociado a una categoría"
)
def create_material(
    material_data: MaterialCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    # Verificar si el código ya existe
    existing = MaterialRepository.get_by_codigo(db, material_data.codigo)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un material con el código '{material_data.codigo}'"
        )
    
    # Verificar que la categoría existe
    categoria = CategoriaRepository.get_by_id(db, material_data.categoria_id)
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoría con ID {material_data.categoria_id} no encontrada"
        )
    
    material = MaterialRepository.create(db, material_data)
    
    return SuccessResponse(
        message="Material creado exitosamente",
        data={
            "id": material.id,
            "codigo": material.codigo,
            "nombre": material.nombre,
            "precio_base": material.precio_base,
            "unidad_medida": material.unidad_medida,
            "categoria_id": material.categoria_id,
            "fecha_creacion": material.fecha_creacion.isoformat()
        }
    )

@router.get(
    "/",
    response_model=SuccessResponse,
    summary="Listar todos los materiales",
    description="Obtiene todos los materiales con opción de filtrar por categoría o buscar"
)
def get_materiales(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=100, description="Número máximo de registros"),
    categoria_id: Optional[int] = Query(None, description="Filtrar por categoría"),
    search: Optional[str] = Query(None, description="Buscar por nombre, código o descripción"),
    db: Session = Depends(get_db)
):
    if search:
        materiales = MaterialRepository.search_by_name(db, search, skip=skip, limit=limit)
    elif categoria_id:
        materiales = MaterialRepository.get_by_categoria(db, categoria_id, skip=skip, limit=limit)
    else:
        materiales = MaterialRepository.get_all_with_categoria(db, skip=skip, limit=limit)
    
    total = MaterialRepository.count(db)
    
    # Convertir a diccionarios con categoría
    materiales_data = []
    for material in materiales:
        material_dict = {
            "id": material.id,
            "codigo": material.codigo,
            "nombre": material.nombre,
            "descripcion": material.descripcion,
            "precio_base": material.precio_base,
            "unidad_medida": material.unidad_medida,
            "imagen_url": material.imagen_url,
            "categoria_id": material.categoria_id,
            "fecha_creacion": material.fecha_creacion.isoformat(),
            "fecha_actualizacion": material.fecha_actualizacion.isoformat()
        }
        
        if hasattr(material, 'categoria') and material.categoria:
            material_dict["categoria"] = {
                "id": material.categoria.id,
                "codigo": material.categoria.codigo,
                "nombre": material.categoria.nombre
            }
        
        materiales_data.append(material_dict)
    
    return SuccessResponse(
        message="Materiales obtenidos exitosamente",
        data={
            "materiales": materiales_data,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    )

@router.get(
    "/{material_id}",
    response_model=SuccessResponse,
    summary="Obtener material por ID",
    description="Obtiene los detalles de un material específico con su categoría"
)
def get_material(
    material_id: int,
    db: Session = Depends(get_db)
):
    material = MaterialRepository.get_by_id_with_categoria(db, material_id)
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Material con ID {material_id} no encontrado"
        )
    
    material_data = {
        "id": material.id,
        "codigo": material.codigo,
        "nombre": material.nombre,
        "descripcion": material.descripcion,
        "precio_base": material.precio_base,
        "unidad_medida": material.unidad_medida,
        "imagen_url": material.imagen_url,
        "categoria_id": material.categoria_id,
        "fecha_creacion": material.fecha_creacion.isoformat(),
        "fecha_actualizacion": material.fecha_actualizacion.isoformat()
    }
    
    if material.categoria:
        material_data["categoria"] = {
            "id": material.categoria.id,
            "codigo": material.categoria.codigo,
            "nombre": material.categoria.nombre,
            "descripcion": material.categoria.descripcion
        }
    
    return SuccessResponse(
        message="Material obtenido exitosamente",
        data=material_data
    )

@router.put(
    "/{material_id}",
    response_model=SuccessResponse,
    summary="Actualizar material",
    description="Actualiza los datos de un material existente"
)
def update_material(
    material_id: int,
    material_data: MaterialUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    # Si se actualiza la categoría, verificar que existe
    if material_data.categoria_id:
        categoria = CategoriaRepository.get_by_id(db, material_data.categoria_id)
        if not categoria:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Categoría con ID {material_data.categoria_id} no encontrada"
            )
    
    material = MaterialRepository.update(db, material_id, material_data)
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Material con ID {material_id} no encontrado"
        )
    
    return SuccessResponse(
        message="Material actualizado exitosamente",
        data={
            "id": material.id,
            "codigo": material.codigo,
            "nombre": material.nombre,
            "precio_base": material.precio_base,
            "unidad_medida": material.unidad_medida,
            "categoria_id": material.categoria_id,
            "fecha_actualizacion": material.fecha_actualizacion.isoformat()
        }
    )

@router.delete(
    "/{material_id}",
    response_model=SuccessResponse,
    summary="Eliminar material",
    description="Elimina un material del sistema"
)
def delete_material(
    material_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    material = MaterialRepository.get_by_id(db, material_id)
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Material con ID {material_id} no encontrado"
        )
    
    success = MaterialRepository.delete(db, material_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al eliminar el material"
        )
    
    return SuccessResponse(
        message="Material eliminado exitosamente",
        data={"id": material_id}
    )
