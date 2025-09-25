# # back-fastapi/auth/register.py
# from fastapi import APIRouter, HTTPException, Depends
# from sqlalchemy.orm import Session
# from pydantic import BaseModel
# from passlib.context import CryptContext
# from database import get_db, get_user_by_username, User

# router = APIRouter()
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# class RegisterRequest(BaseModel):
#     username: str
#     password: str

# @router.post("/register")
# def register(request: RegisterRequest, db: Session = Depends(get_db)):
#     user = get_user_by_username(db, request.username)
#     if user:
#         raise HTTPException(status_code=400, detail="El usuario ya existe")
    
#     hashed_password = pwd_context.hash(request.password)
#     new_user = User(username=request.username, password=hashed_password)
#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)
    
#     return {"message": f"Usuario {new_user.username} registrado con éxito"}

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from passlib.context import CryptContext
from database import get_db
from repositories.user_repository import get_user_by_username
from models.usuario import Usuario
from fastapi.responses import JSONResponse
from jose import jwt
from config import settings
from datetime import datetime, timedelta

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class RegisterRequest(BaseModel):
    correo: str
    contrasena: str
    nombre: str

# Función para crear el token JWT
def create_token(data: dict):
    data_token = data.copy()
    data_token["exp"] = datetime.utcnow() + timedelta(seconds=int(settings.TOKEN_SECONDS_EXP))
    return jwt.encode(data_token, key=settings.SECRET_KEY, algorithm=settings.ALGORITHM)

@router.post("/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    user = get_user_by_username(db, request.correo)
    if user:
        raise HTTPException(status_code=400, detail="El usuario ya existe")

    hashed_password = pwd_context.hash(request.contrasena)
    new_user = Usuario(correo=request.correo, contrasena=hashed_password, nombre=request.nombre)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Crear el token al registrarse
    token = create_token({"sub": new_user.correo})

    return JSONResponse(content={"message": f"Usuario {new_user.correo} registrado con éxito", "access_token": token, "token_type": "bearer"})

