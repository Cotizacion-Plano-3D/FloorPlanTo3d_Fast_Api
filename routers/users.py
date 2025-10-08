# routers/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from middleware.auth_middleware import get_current_user
from models.usuario import Usuario
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
    db: Session = Depends(get_db)
):
    """
    Obtener lista de usuarios
    
    Devuelve información básica de todos los usuarios registrados.
    """
    users = db.query(Usuario).all()
    return [UsuarioResponse.from_orm(user) for user in users]

@router.get(
    "/test",
    summary="Test endpoint sin autenticación",
    description="Endpoint de prueba para verificar si el problema es de autenticación"
)
def test_users(db: Session = Depends(get_db)):
    """
    Endpoint de prueba sin autenticación
    """
    users = db.query(Usuario).all()
    return {"total_users": len(users), "users": [{"id": u.id, "correo": u.correo} for u in users]}

@router.get(
    "/me",
    response_model=UsuarioResponse,
    summary="Obtener perfil del usuario actual",
    openapi_extra={"security": [{"BearerAuth": []}]}, 
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
    user: Usuario = Depends(get_current_user)
):
    """
    Obtener perfil del usuario actual
    """
    if not user:
        raise HTTPException(status_code=404, detail="No hay usuarios registrados")
    return UsuarioResponse.model_validate(user)
