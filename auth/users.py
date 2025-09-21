from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db, User

router = APIRouter()

@router.get("/users")
def get_users(db: Session = Depends(get_db)):
    """Este endpoint devuelve todos los usuarios registrados."""
    users = db.query(User).all()
    return {"users": users}
