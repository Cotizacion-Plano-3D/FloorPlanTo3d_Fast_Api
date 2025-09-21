from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from passlib.context import CryptContext
from database import get_db, get_user_by_username, User
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from config import settings

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# Pydantic model para la solicitud de cambio de contraseña
class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

# Verifica el token y extrae el usuario
def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, key=settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        return username
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

# Endpoint para cambiar la contraseña
@router.post("/change-password")
def change_password(request: ChangePasswordRequest, db: Session = Depends(get_db), username: str = Depends(verify_token)):
    user = get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Verificar la contraseña actual
    if not pwd_context.verify(request.current_password, user.password):
        raise HTTPException(status_code=400, detail="Contraseña actual incorrecta")
    
    # Encriptar la nueva contraseña
    hashed_password = pwd_context.hash(request.new_password)
    
    # Actualizar la contraseña en la base de datos
    user.password = hashed_password
    db.commit()
    db.refresh(user)
    
    return {"message": "Contraseña actualizada con éxito"}
