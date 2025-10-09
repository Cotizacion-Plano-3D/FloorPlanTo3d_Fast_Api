from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from services.pago_service import (
    list_pagos, get_pago, add_pago, edit_pago, remove_pago
)
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/pagos", tags=["Pagos"])

class PagoCreate(BaseModel):
    suscripcion_id: int
    monto: float
    moneda: str
    metodo: str
    estado: str
    referencia_pasarela: Optional[str] = None
    fecha_pago: Optional[str] = None

@router.get("/")
def get_pagos(db: Session = Depends(get_db)):
    return list_pagos(db)

@router.get("/{pago_id}")
def get_pago_by_id(pago_id: int, db: Session = Depends(get_db)):
    pago = get_pago(db, pago_id)
    if not pago:
        raise HTTPException(status_code=404, detail="Pago no encontrado")
    return pago

@router.post("/")
def create_pago(pago: PagoCreate, db: Session = Depends(get_db)):
    return add_pago(db, pago.dict())

@router.put("/{pago_id}")
def update_pago(pago_id: int, pago: PagoCreate, db: Session = Depends(get_db)):
    updated = edit_pago(db, pago_id, pago.dict())
    if not updated:
        raise HTTPException(status_code=404, detail="Pago no encontrado")
    return updated

@router.delete("/{pago_id}")
def delete_pago(pago_id: int, db: Session = Depends(get_db)):
    deleted = remove_pago(db, pago_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Pago no encontrado")
    return {"detail": "Pago eliminado"}
