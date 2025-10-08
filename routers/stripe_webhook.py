# routers/stripe_webhook.py
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
    print("🔔 WEBHOOK RECIBIDO - Iniciando procesamiento...")
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    print(f"📋 Headers recibidos: {dict(request.headers)}")
    print(f"📦 Payload size: {len(payload)} bytes")
    
    event = None
    if sig_header:
        print("🔐 Validando firma del webhook...")
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, STRIPE_WEBHOOK_SECRET
            )
            print("✅ Firma del webhook validada correctamente")
        except Exception as e:
            print(f"❌ Error validando webhook: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Webhook error: {str(e)}")
    else:
        print("⚠️ Sin firma de webhook - modo desarrollo")
        # Permitir pruebas locales sin validación de firma
        import json
        event = json.loads(payload)
    
    print(f"📨 Tipo de evento: {event.get('type', 'unknown')}")
    print(f"📨 ID del evento: {event.get('id', 'unknown')}")

    # Maneja el evento de suscripción exitosa
    if event['type'] == 'checkout.session.completed':
        print("🎉 EVENTO: checkout.session.completed detectado")
        session = event['data']['object']
        print(f"📧 Email del cliente: {session.get('customer_email')}")
        print(f"📦 Metadatos: {session.get('metadata', {})}")
        
        # Recupera el email del usuario y el membresia_id de los metadatos
        email = session.get('customer_email')
        metadata = session.get('metadata', {})
        membresia_id = metadata.get('membresia_id')
        
        print(f"🔍 Buscando usuario con email: {email}")
        print(f"🔍 Membresia ID: {membresia_id}")
        
        if not membresia_id:
            print("❌ ERROR: No membresia_id found in metadata")
            return JSONResponse({"status": "error", "message": "No membresia_id found in metadata"})
        
        # Busca el usuario y la membresía
        usuario = db.query(Usuario).filter(Usuario.correo == email).first()
        membresia = db.query(Membresia).filter(Membresia.id == int(membresia_id)).first()
        
        print(f"👤 Usuario encontrado: {usuario.id if usuario else 'No encontrado'}")
        print(f"📋 Membresía encontrada: {membresia.nombre if membresia else 'No encontrada'}")
        
        if usuario and membresia:
            print("✅ Creando suscripción...")
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
            print(f"🎉 Suscripción creada con ID: {nueva_suscripcion.id}")
            return JSONResponse({"status": "success", "suscripcion_id": nueva_suscripcion.id})
        else:
            print("❌ ERROR: Usuario o membresía no encontrados")
            return JSONResponse({"status": "error", "message": "Usuario o membresía no encontrados"})
    else:
        print(f"ℹ️ Evento ignorado: {event['type']}")
    
    return JSONResponse({"status": "ignored"})
