from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from config import settings

from models import Base, Usuario, Membresia, Suscripcion, Pago

DATABASE_URL = f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear tablas automáticamente (asegúrate de importar todos los modelos en algún lugar central)
Base.metadata.create_all(bind=engine)

# Dependencia para inyectar sesión DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

