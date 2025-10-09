# routers/stripe_create_membresia.py
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import stripe
from config import settings
from database import get_db
from models.membresia import Membresia
from models.suscripcion import Suscripcion
from models.usuario import Usuario
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/stripe", tags=["stripe"])

stripe.api_key = settings.STRIPE_SECRET_KEY

class SuscripcionCreateRequest(BaseModel):
    usuario_id: int
    membresia_id: int

@router.post("/create-suscripcion-stripe")
async def create_suscripcion_stripe(req: SuscripcionCreateRequest, db=Depends(get_db)):
    try:
        usuario = db.query(Usuario).filter(Usuario.id == req.usuario_id).first()
        membresia = db.query(Membresia).filter(Membresia.id == req.membresia_id).first()
        if not usuario or not membresia:
            raise HTTPException(status_code=404, detail="Usuario o membresía no encontrada")
        nueva_suscripcion = Suscripcion(
            usuario_id=usuario.id,
            membresia_id=membresia.id,
            fecha_inicio=datetime.utcnow(),
            fecha_fin=datetime.utcnow() + timedelta(days=membresia.duracion),
            estado='activa'
        )
        db.add(nueva_suscripcion)
        db.commit()
        db.refresh(nueva_suscripcion)
        return JSONResponse({"id": nueva_suscripcion.id, "usuario_id": usuario.id, "membresia_id": membresia.id})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
