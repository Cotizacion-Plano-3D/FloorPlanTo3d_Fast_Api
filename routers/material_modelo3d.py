from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from repositories.material_modelo3d_repository import MaterialModelo3DRepository
from repositories.material_repository import MaterialRepository
from repositories.modelo3d_repository import Modelo3DRepository
from schemas.material_modelo3d_schemas import (
    MaterialModelo3DCreate, 
    MaterialModelo3DUpdate, 
    MaterialModelo3DResponse,
    MaterialModelo3DConDetalles,
    ResumenCostosMateriales
)
from schemas.response_schemas import SuccessResponse
from middleware.auth_middleware import get_current_user
from models.usuario import Usuario

router = APIRouter(
    prefix="/materiales-modelo3d",
    tags=["Materiales Modelo 3D"]
)

@router.post(
    "/",
    response_model=SuccessResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Agregar material a modelo 3D",
    description="Asocia un material con un modelo 3D especificando cantidad y precio"
)
def add_material_to_modelo3d(
    material_data: MaterialModelo3DCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    # Verificar que el modelo 3D existe
    modelo3d = Modelo3DRepository.get_by_id(db, material_data.modelo3d_id)
    if not modelo3d:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Modelo 3D con ID {material_data.modelo3d_id} no encontrado"
        )
    
    # Verificar que el material existe
    material = MaterialRepository.get_by_id(db, material_data.material_id)
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Material con ID {material_data.material_id} no encontrado"
        )
    
    material_modelo3d = MaterialModelo3DRepository.create(db, material_data)
    
    return SuccessResponse(
        message="Material agregado al modelo 3D exitosamente",
        data={
            "id": material_modelo3d.id,
            "modelo3d_id": material_modelo3d.modelo3d_id,
            "material_id": material_modelo3d.material_id,
            "cantidad": material_modelo3d.cantidad,
            "unidad_medida": material_modelo3d.unidad_medida,
            "precio_unitario": material_modelo3d.precio_unitario,
            "subtotal": material_modelo3d.subtotal
        }
    )

@router.post(
    "/bulk",
    response_model=SuccessResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Agregar múltiples materiales",
    description="Asocia múltiples materiales con un modelo 3D en una sola operación"
)
def add_materials_bulk(
    materiales_data: List[MaterialModelo3DCreate],
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    if not materiales_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe proporcionar al menos un material"
        )
    
    # Verificar que todos los materiales y modelos existen
    for material_data in materiales_data:
        modelo3d = Modelo3DRepository.get_by_id(db, material_data.modelo3d_id)
        if not modelo3d:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Modelo 3D con ID {material_data.modelo3d_id} no encontrado"
            )
        
        material = MaterialRepository.get_by_id(db, material_data.material_id)
        if not material:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Material con ID {material_data.material_id} no encontrado"
            )
    
    materiales_modelo3d = MaterialModelo3DRepository.create_bulk(db, materiales_data)
    
    return SuccessResponse(
        message=f"{len(materiales_modelo3d)} materiales agregados exitosamente",
        data={
            "total": len(materiales_modelo3d),
            "materiales": [
                {
                    "id": m.id,
                    "material_id": m.material_id,
                    "cantidad": m.cantidad,
                    "subtotal": m.subtotal
                } for m in materiales_modelo3d
            ]
        }
    )

@router.get(
    "/modelo3d/{modelo3d_id}",
    response_model=SuccessResponse,
    summary="Obtener materiales de un modelo 3D",
    description="Obtiene todos los materiales asociados a un modelo 3D con sus detalles"
)
def get_materiales_by_modelo3d(
    modelo3d_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    # Verificar que el modelo 3D existe
    modelo3d = Modelo3DRepository.get_by_id(db, modelo3d_id)
    if not modelo3d:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Modelo 3D con ID {modelo3d_id} no encontrado"
        )
    
    materiales = MaterialModelo3DRepository.get_by_modelo3d_with_details(db, modelo3d_id)
    
    materiales_data = []
    for mat in materiales:
        mat_dict = {
            "id": mat.id,
            "modelo3d_id": mat.modelo3d_id,
            "material_id": mat.material_id,
            "cantidad": mat.cantidad,
            "unidad_medida": mat.unidad_medida,
            "precio_unitario": mat.precio_unitario,
            "subtotal": mat.subtotal
        }
        
        if mat.material:
            mat_dict["material"] = {
                "id": mat.material.id,
                "codigo": mat.material.codigo,
                "nombre": mat.material.nombre,
                "descripcion": mat.material.descripcion,
                "imagen_url": mat.material.imagen_url
            }
            
            if mat.material.categoria:
                mat_dict["material"]["categoria"] = {
                    "id": mat.material.categoria.id,
                    "nombre": mat.material.categoria.nombre
                }
        
        materiales_data.append(mat_dict)
    
    total_costo = MaterialModelo3DRepository.get_total_cost(db, modelo3d_id)
    
    return SuccessResponse(
        message="Materiales obtenidos exitosamente",
        data={
            "modelo3d_id": modelo3d_id,
            "total_materiales": len(materiales),
            "costo_total": total_costo,
            "materiales": materiales_data
        }
    )

@router.get(
    "/{material_modelo3d_id}",
    response_model=SuccessResponse,
    summary="Obtener detalle de material-modelo3d",
    description="Obtiene los detalles de una relación específica material-modelo3d"
)
def get_material_modelo3d(
    material_modelo3d_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    material_modelo3d = MaterialModelo3DRepository.get_by_id_with_details(db, material_modelo3d_id)
    if not material_modelo3d:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Relación con ID {material_modelo3d_id} no encontrada"
        )
    
    return SuccessResponse(
        message="Detalle obtenido exitosamente",
        data={
            "id": material_modelo3d.id,
            "modelo3d_id": material_modelo3d.modelo3d_id,
            "material_id": material_modelo3d.material_id,
            "cantidad": material_modelo3d.cantidad,
            "unidad_medida": material_modelo3d.unidad_medida,
            "precio_unitario": material_modelo3d.precio_unitario,
            "subtotal": material_modelo3d.subtotal
        }
    )

@router.put(
    "/{material_modelo3d_id}",
    response_model=SuccessResponse,
    summary="Actualizar material en modelo 3D",
    description="Actualiza la cantidad o precio de un material en un modelo 3D"
)
def update_material_modelo3d(
    material_modelo3d_id: int,
    material_data: MaterialModelo3DUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    material_modelo3d = MaterialModelo3DRepository.update(db, material_modelo3d_id, material_data)
    if not material_modelo3d:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Relación con ID {material_modelo3d_id} no encontrada"
        )
    
    return SuccessResponse(
        message="Material actualizado exitosamente",
        data={
            "id": material_modelo3d.id,
            "cantidad": material_modelo3d.cantidad,
            "precio_unitario": material_modelo3d.precio_unitario,
            "subtotal": material_modelo3d.subtotal
        }
    )

@router.delete(
    "/{material_modelo3d_id}",
    response_model=SuccessResponse,
    summary="Eliminar material de modelo 3D",
    description="Elimina la asociación de un material con un modelo 3D"
)
def delete_material_modelo3d(
    material_modelo3d_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    material_modelo3d = MaterialModelo3DRepository.get_by_id(db, material_modelo3d_id)
    if not material_modelo3d:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Relación con ID {material_modelo3d_id} no encontrada"
        )
    
    success = MaterialModelo3DRepository.delete(db, material_modelo3d_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al eliminar la relación"
        )
    
    return SuccessResponse(
        message="Material eliminado del modelo 3D exitosamente",
        data={"id": material_modelo3d_id}
    )
