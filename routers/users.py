# routers/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.usuario import Usuario
from middleware.auth_middleware import get_current_user
from schemas import UsuarioResponse, ErrorResponse
from typing import List

router = APIRouter(
    prefix="/users",
    tags=["Usuarios"],
    responses={
        401: {"model": ErrorResponse, "description": "Token de autenticación inválido"},
        403: {"model": ErrorResponse, "description": "Acceso denegado - Solo administradores"}
    }
)

@router.get(
    "/",
    response_model=List[UsuarioResponse],
    summary="Listar todos los usuarios",
    description="""
    Obtiene una lista de todos los usuarios registrados en el sistema.
    
    **⚠️ Requiere autenticación:** Sí
    **🔒 Permisos:** Solo usuarios autenticados
    
    **Información devuelta:**
    - ID único del usuario
    - Nombre completo
    - Correo electrónico
    - Fecha de registro
    
    **Nota:** Este endpoint está protegido y requiere un token JWT válido.
    """,
    responses={
        200: {
            "description": "Lista de usuarios obtenida exitosamente",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 1,
                            "nombre": "Juan Pérez",
                            "correo": "juan.perez@email.com",
                            "fecha_creacion": "2024-01-15T10:30:00Z"
                        },
                        {
                            "id": 2,
                            "nombre": "María García",
                            "correo": "maria.garcia@email.com",
                            "fecha_creacion": "2024-01-16T14:20:00Z"
                        }
                    ]
                }
            }
        }
    }
)
def get_users(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener lista de usuarios
    
    Devuelve información básica de todos los usuarios registrados.
    Requiere autenticación JWT válida.
    """
    users = db.query(Usuario).all()
    return [UsuarioResponse.from_orm(user) for user in users]

@router.get(
    "/me",
    response_model=UsuarioResponse,
    summary="Obtener perfil del usuario actual",
    description="""
    Obtiene la información del perfil del usuario autenticado.
    
    **⚠️ Requiere autenticación:** Sí
    **🔒 Permisos:** Usuario autenticado (propio perfil)
    
    **Información devuelta:**
    - Datos personales del usuario autenticado
    - Información de registro
    """,
    responses={
        200: {
            "description": "Perfil del usuario obtenido exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "nombre": "Juan Pérez",
                        "correo": "juan.perez@email.com",
                        "fecha_creacion": "2024-01-15T10:30:00Z"
                    }
                }
            }
        }
    }
)
def get_current_user_profile(
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener perfil del usuario actual
    
    Devuelve la información del usuario autenticado.
    """
    return UsuarioResponse.from_orm(current_user)
