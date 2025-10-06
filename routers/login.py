# routers/login.py
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from jose import jwt
from datetime import datetime, timedelta
import hashlib
from database import get_db
from repositories.user_repository import get_user_by_username
from config import settings
from schemas import LoginRequest, TokenResponse, ErrorResponse

router = APIRouter(
    prefix="/auth",
    tags=["Autenticación"],
    responses={
        401: {"model": ErrorResponse, "description": "Credenciales incorrectas"},
        422: {"model": ErrorResponse, "description": "Error de validación"}
    }
)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password

def authenticate_user(db: Session, correo: str, contrasena: str):
    user = get_user_by_username(db, correo)
    if not user:
        return False
    
    if not verify_password(contrasena, user.contrasena):
        return False
    return user

def create_token(data: dict):
    data_token = data.copy()
    data_token["exp"] = datetime.utcnow() + timedelta(seconds=int(settings.TOKEN_SECONDS_EXP))
    return jwt.encode(data_token, key=settings.SECRET_KEY, algorithm=settings.ALGORITHM)

@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Iniciar sesión",
    description="""
    Autentica a un usuario y devuelve un token JWT.
    
    **Ejemplo de uso:**
    1. Proporciona tu correo y contraseña
    2. Recibe un token JWT válido
    3. Usa el token en el header `Authorization: Bearer <token>` para endpoints protegidos
    """,
    responses={
        200: {
            "description": "Login exitoso",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer"
                    }
                }
            }
        }
    }
)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Iniciar sesión de usuario
    
    - **correo**: Correo electrónico del usuario
    - **contrasena**: Contraseña del usuario
    
    Devuelve un token JWT que debe ser incluido en el header Authorization para endpoints protegidos.
    """
    user = authenticate_user(db, request.correo, request.contrasena)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Usuario o contraseña incorrectos"
        )

    token = create_token({"sub": user.correo})
    return TokenResponse(access_token=token, token_type="bearer")
