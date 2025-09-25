from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from services.membresia_service import (
    list_membresias, get_membresia, add_membresia, edit_membresia, remove_membresia
)
from pydantic import BaseModel

router = APIRouter(prefix="/membresias", tags=["Membresias"])

class MembresiaCreate(BaseModel):
    nombre: str
    precio: float
    duracion: int
    descripcion: str = None

@router.get("/")
def get_membresias(db: Session = Depends(get_db)):
    return list_membresias(db)

@router.get("/{membresia_id}")
def get_membresia_by_id(membresia_id: int, db: Session = Depends(get_db)):
    membresia = get_membresia(db, membresia_id)
    if not membresia:
        raise HTTPException(status_code=404, detail="Membresía no encontrada")
    return membresia

@router.post("/")
def create_membresia(membresia: MembresiaCreate, db: Session = Depends(get_db)):
    return add_membresia(db, membresia.dict())

@router.put("/{membresia_id}")
def update_membresia(membresia_id: int, membresia: MembresiaCreate, db: Session = Depends(get_db)):
    updated = edit_membresia(db, membresia_id, membresia.dict())
    if not updated:
        raise HTTPException(status_code=404, detail="Membresía no encontrada")
    return updated

@router.delete("/{membresia_id}")
def delete_membresia(membresia_id: int, db: Session = Depends(get_db)):
    deleted = remove_membresia(db, membresia_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Membresía no encontrada")
    return {"detail": "Membresía eliminada"}
