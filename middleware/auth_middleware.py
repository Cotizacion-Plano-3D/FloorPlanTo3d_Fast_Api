# middleware/auth_middleware.py
"""
Middleware de autenticación JWT para FastAPI
"""

from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from database import get_db
from repositories.user_repository import get_user_by_username
from config import settings

# Configurar HTTPBearer para extraer el token del header Authorization
security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Extrae y valida el token JWT del header Authorization
    Devuelve el usuario autenticado
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    print(f"DEBUG: Token recibido: {credentials.credentials[:20]}...")
    
    try:
        # Decodificar el token JWT
        payload = jwt.decode(
            credentials.credentials, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        print(f"DEBUG: Payload decodificado: {payload}")
        correo: str = payload.get("sub")
        print(f"DEBUG: Correo extraído: {correo}")
        if correo is None:
            print("DEBUG: Error - correo es None")
            raise credentials_exception
    except JWTError as e:
        print(f"DEBUG: Error JWT: {e}")
        raise credentials_exception
    
    # Buscar el usuario en la base de datos
    print(f"DEBUG: Buscando usuario con correo: {correo}")
    user = get_user_by_username(db, correo)
    print(f"DEBUG: Usuario encontrado: {user is not None}")
    if user is None:
        print("DEBUG: Error - usuario no encontrado en BD")
        raise credentials_exception
    
    print(f"DEBUG: Usuario autenticado exitosamente: {user.correo}")
    return user

def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Versión opcional de get_current_user que no falla si no hay token
    Útil para endpoints que pueden funcionar con o sin autenticación
    """
    try:
        return get_current_user(credentials, db)
    except HTTPException:
        return None
