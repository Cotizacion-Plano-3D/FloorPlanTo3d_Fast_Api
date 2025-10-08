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
    
    print(f"[AUTH] Token recibido: {credentials.credentials}")
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        print(f"[AUTH] Payload decodificado: {payload}")
        correo: str = payload.get("sub")
        print(f"[AUTH] Claim 'sub' extraído: {correo}")
        if correo is None:
            print("[AUTH] ERROR: Claim 'sub' es None")
            raise credentials_exception
    except JWTError as e:
        print(f"[AUTH] ERROR: JWT inválido: {e}")
        raise credentials_exception

    print(f"[AUTH] Buscando usuario en BD con correo: {correo}")
    user = get_user_by_username(db, correo)
    if user:
        print(f"[AUTH] Usuario encontrado: id={user.id}, correo={user.correo}")
    else:
        print(f"[AUTH] ERROR: Usuario no encontrado en BD para correo: {correo}")
        raise credentials_exception

    print(f"[AUTH] Usuario autenticado exitosamente: {user.correo}")
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
