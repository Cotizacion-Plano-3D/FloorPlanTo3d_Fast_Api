from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from jose import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from database import get_db, get_user_by_username
from config import settings

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class LoginRequest(BaseModel):
    username: str
    password: str

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not pwd_context.verify(password, user.password):
        return False
    return user

def create_token(data: dict):
    data_token = data.copy()
    data_token["exp"] = datetime.utcnow() + timedelta(seconds=int(settings.TOKEN_SECONDS_EXP))
    return jwt.encode(data_token, key=settings.SECRET_KEY, algorithm=settings.ALGORITHM)

@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, request.username, request.password)
    if not user:
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")
    
    token = create_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}
