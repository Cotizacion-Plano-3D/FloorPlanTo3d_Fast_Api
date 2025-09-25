from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.usuario import Usuario

router = APIRouter()

@router.get("/users")
def get_users(db: Session = Depends(get_db)):
    """Este endpoint devuelve todos los usuarios registrados."""
    users = db.query(Usuario).all()
    return {"users": users}
