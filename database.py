from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from config import settings

from models import Base, Usuario, Membresia, Suscripcion, Pago

DATABASE_URL = f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verifica conexiones antes de usarlas
    pool_recycle=300,    # Recicla conexiones cada 5 minutos
    echo=False           # Cambia a True para ver las consultas SQL
)
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

