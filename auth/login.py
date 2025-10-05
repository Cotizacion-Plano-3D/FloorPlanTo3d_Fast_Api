# back-fastapi/auth/login.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from jose import jwt
from datetime import datetime, timedelta
import hashlib
from database import get_db
from repositories.user_repository import get_user_by_username
from config import settings

router = APIRouter()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password

class LoginRequest(BaseModel):
    correo: str
    contrasena: str

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

@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, request.correo, request.contrasena)
    if not user:
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")

    token = create_token({"sub": user.correo})
    return {"access_token": token, "token_type": "bearer"}
