from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
import stripe
from config import settings
from database import get_db
from models.suscripcion import Suscripcion
from models.membresia import Membresia
from models.usuario import Usuario
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/stripe", tags=["stripe"])

stripe.api_key = settings.STRIPE_SECRET_KEY

# Debes configurar tu endpoint secret en Stripe dashboard
STRIPE_WEBHOOK_SECRET = settings.STRIPE_WEBHOOK_SECRET if hasattr(settings, 'STRIPE_WEBHOOK_SECRET') else "whsec_xxxxxxxxxxxxx"

@router.post("/webhook")
async def stripe_webhook(request: Request, db=Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    event = None
    if sig_header:
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, STRIPE_WEBHOOK_SECRET
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Webhook error: {str(e)}")
    else:
        # Permitir pruebas locales sin validación de firma
        import json
        event = json.loads(payload)

    # Maneja el evento de suscripción exitosa
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        # Recupera el email del usuario
        email = session.get('customer_email')
        price_id = session['display_items'][0]['price']['id'] if 'display_items' in session else None
        # Busca el usuario y la membresía
        usuario = db.query(Usuario).filter(Usuario.correo == email).first()
        membresia = db.query(Membresia).filter(Membresia.stripe_price_id == price_id).first()
        if usuario and membresia:
            # Crea la suscripción
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
            return JSONResponse({"status": "success"})
    return JSONResponse({"status": "ignored"})
