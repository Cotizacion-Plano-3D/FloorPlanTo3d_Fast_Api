from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from services.suscripcion_service import (
    list_suscripciones, get_suscripcion, add_suscripcion, edit_suscripcion, remove_suscripcion
)
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/suscripciones", tags=["Suscripciones"])

class SuscripcionCreate(BaseModel):
    usuario_id: int
    membresia_id: int
    fecha_inicio: str
    fecha_fin: str
    estado: str

@router.get("/")
def get_suscripciones(db: Session = Depends(get_db)):
    return list_suscripciones(db)

@router.get("/{suscripcion_id}")
def get_suscripcion_by_id(suscripcion_id: int, db: Session = Depends(get_db)):
    suscripcion = get_suscripcion(db, suscripcion_id)
    if not suscripcion:
        raise HTTPException(status_code=404, detail="Suscripción no encontrada")
    return suscripcion

@router.post("/")
def create_suscripcion(suscripcion: SuscripcionCreate, db: Session = Depends(get_db)):
    return add_suscripcion(db, suscripcion.dict())

@router.put("/{suscripcion_id}")
def update_suscripcion(suscripcion_id: int, suscripcion: SuscripcionCreate, db: Session = Depends(get_db)):
    updated = edit_suscripcion(db, suscripcion_id, suscripcion.dict())
    if not updated:
        raise HTTPException(status_code=404, detail="Suscripción no encontrada")
    return updated

@router.delete("/{suscripcion_id}")
def delete_suscripcion(suscripcion_id: int, db: Session = Depends(get_db)):
    deleted = remove_suscripcion(db, suscripcion_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Suscripción no encontrada")
    return {"detail": "Suscripción eliminada"}
