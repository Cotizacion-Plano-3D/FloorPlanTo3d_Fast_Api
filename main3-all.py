from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from jose import jwt, JWTError
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from passlib.context import CryptContext

# main.py de FastAPI
from fastapi.middleware.cors import CORSMiddleware

# --- Configuración JWT ---
SECRET_KEY = "fdbc6d8866883c545601dc0617b8e0ae6404ad9291376c64533844a2504ee0eb"
ALGORITHM = "HS256"
TOKEN_SECONDS_EXP = 300

# --- Configuración BD ---
DATABASE_URL = "postgresql://postgres:admin@localhost:5432/fastapi"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Modelo User ---
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

# --- Seguridad ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# --- FastAPI App ---
app = FastAPI()

# --- Schemas ---
class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str

# --- Dependencia de sesión ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Utilidades ---
def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not pwd_context.verify(password, user.password):
        return False
    return user

def create_token(data: dict):
    data_token = data.copy()
    data_token["exp"] = datetime.utcnow() + timedelta(seconds=TOKEN_SECONDS_EXP)
    return jwt.encode(data_token, key=SECRET_KEY, algorithm=ALGORITHM)

# --- Endpoints ---
@app.post("/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    user = get_user_by_username(db, request.username)
    if user:
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    
    hashed_password = pwd_context.hash(request.password)
    new_user = User(username=request.username, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": f"Usuario {new_user.username} registrado con éxito"}

@app.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, request.username, request.password)
    if not user:
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")
    
    token = create_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

@app.get("/users/dashboard")
def dashboard(username: str = Depends(verify_token)):
    return {"message": f"Bienvenido {username} al dashboard!"}

origins = [
    "http://localhost:5173",  # URL de tu frontend React
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,   # permite estas URLs
    allow_credentials=True,
    allow_methods=["*"],     # permite GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],     # permite headers personalizados
)