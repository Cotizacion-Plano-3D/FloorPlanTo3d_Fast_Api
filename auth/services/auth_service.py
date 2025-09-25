from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from config import settings
from auth.repositories.user_repository import get_user_by_username

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Autenticación de usuario

def authenticate_user(db, username, password):
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not pwd_context.verify(password, user.contrasena):
        return False
    return user

# Crear token JWT

def create_token(data: dict):
    data_token = data.copy()
    data_token["exp"] = datetime.utcnow() + timedelta(seconds=int(settings.TOKEN_SECONDS_EXP))
    return jwt.encode(data_token, key=settings.SECRET_KEY, algorithm=settings.ALGORITHM)
