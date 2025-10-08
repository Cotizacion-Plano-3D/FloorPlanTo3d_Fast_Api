# routers/stripe.py
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import stripe
from fastapi import Depends
from database import get_db
from models.membresia import Membresia
from config import settings
from middleware.auth_middleware import get_current_user
from models.usuario import Usuario

# Configura tu clave secreta de Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

router = APIRouter(prefix="/api/stripe", tags=["stripe"])

class CheckoutSessionRequest(BaseModel):
    membresia_id: int

@router.post("/create-checkout-session")
async def create_checkout_session(req: CheckoutSessionRequest, db=Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    membresia = db.query(Membresia).filter(Membresia.id == req.membresia_id).first()
    if not membresia:
        raise HTTPException(status_code=404, detail="Membresía no encontrada")
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": membresia.nombre,
                        "description": membresia.descripcion
                    },
                    "unit_amount": int(membresia.precio * 100),
                },
                "quantity": 1,
            }],
            mode="payment",
            customer_email=current_user.correo,
            metadata={
                "membresia_id": str(membresia.id),
                "membresia_nombre": membresia.nombre
            },
            success_url=f"{settings.FRONTEND_URL}/dashboard?success=true",
            cancel_url=f"{settings.FRONTEND_URL}/dashboard?canceled=true",
        )
        return JSONResponse({"id": session.id, "url": session.url})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
