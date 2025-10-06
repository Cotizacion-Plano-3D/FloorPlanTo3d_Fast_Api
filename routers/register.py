# routers/register.py
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
import hashlib
from database import get_db
from repositories.user_repository import get_user_by_username
from models.usuario import Usuario
from fastapi.responses import JSONResponse
from jose import jwt
from config import settings
from datetime import datetime, timedelta
from schemas import RegisterRequest, RegisterResponse, ErrorResponse

router = APIRouter(
    prefix="/auth",
    tags=["Autenticación"],
    responses={
        400: {"model": ErrorResponse, "description": "Usuario ya existe"},
        422: {"model": ErrorResponse, "description": "Error de validación"}
    }
)

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password

# Función para crear el token JWT
def create_token(data: dict):
    data_token = data.copy()
    data_token["exp"] = datetime.utcnow() + timedelta(seconds=int(settings.TOKEN_SECONDS_EXP))
    return jwt.encode(data_token, key=settings.SECRET_KEY, algorithm=settings.ALGORITHM)

@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nuevo usuario",
    description="""
    Registra un nuevo usuario en el sistema y devuelve un token JWT automáticamente.
    
    **Características:**
    - Crea una nueva cuenta de usuario
    - Valida que el correo no esté en uso
    - Devuelve un token JWT para autenticación inmediata
    - La contraseña se almacena de forma segura (hash SHA-256)
    """,
    responses={
        201: {
            "description": "Usuario registrado exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Usuario juan.perez@email.com registrado con éxito",
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer"
                    }
                }
            }
        }
    }
)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    Registrar nuevo usuario
    
    - **correo**: Correo electrónico único del usuario
    - **contrasena**: Contraseña (mínimo 6 caracteres)
    - **nombre**: Nombre completo del usuario
    
    Devuelve un token JWT que permite acceso inmediato sin necesidad de login adicional.
    """
    user = get_user_by_username(db, request.correo)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="El usuario ya existe"
        )

    hashed_password = hash_password(request.contrasena)
    new_user = Usuario(correo=request.correo, contrasena=hashed_password, nombre=request.nombre)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Crear el token al registrarse
    token = create_token({"sub": new_user.correo})

    return RegisterResponse(
        message=f"Usuario {new_user.correo} registrado con éxito",
        access_token=token,
        token_type="bearer"
    )
