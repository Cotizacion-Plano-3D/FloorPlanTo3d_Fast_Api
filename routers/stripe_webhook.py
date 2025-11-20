from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from database import get_db
from models.usuario import Usuario
from models.membresia import Membresia
from models.suscripcion import Suscripcion
from models.pago import Pago
from config import settings
from datetime import datetime, timedelta
import stripe
import logging
import traceback

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/stripe", tags=["stripe-webhook"])
stripe.api_key = settings.STRIPE_SECRET_KEY

@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    
    logger.info("=" * 80)
    logger.info("[WEBHOOK] Webhook recibido de Stripe")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, 
            sig_header, 
            settings.STRIPE_WEBHOOK_SECRET
        )
        logger.info(f"[OK] Evento validado: {event['type']}")
        logger.info(f"[EVENT_ID] {event['id']}")
        
    except ValueError as e:
        logger.error(f"[ERROR] Payload invalido: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"[ERROR] Firma invalida: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Manejar checkout completado
    if event['type'] == 'checkout.session.completed':
        try:
            session = event['data']['object']
            
            logger.info(f"[CHECKOUT] Procesando checkout.session.completed")
            logger.info(f"[SESSION_ID] {session['id']}")
            
            # Extraer y loggear TODOS los datos
            email = session.get('customer_email')
            metadata = session.get('metadata', {})
            membresia_id = metadata.get('membresia_id')
            usuario_id = metadata.get('usuario_id')
            amount_total = session.get('amount_total', 0)
            currency = session.get('currency', 'usd')
            payment_status = session.get('payment_status')
            
            logger.info(f"[DATA] Email: {email}")
            logger.info(f"[DATA] Membresia ID: {membresia_id}")
            logger.info(f"[DATA] Usuario ID: {usuario_id}")
            logger.info(f"[DATA] Amount: {amount_total} (centavos)")
            logger.info(f"[DATA] Currency: {currency}")
            logger.info(f"[DATA] Payment Status: {payment_status}")
            logger.info(f"[METADATA] Completa: {metadata}")
            
            # Validar datos requeridos
            if not email:
                logger.error("[ERROR] Falta customer_email en session")
                raise ValueError("Missing customer_email")
            
            if not membresia_id:
                logger.error("[ERROR] Falta membresia_id en metadata")
                raise ValueError("Missing membresia_id in metadata")
            
            # Buscar usuario
            logger.info(f"[DB] Buscando usuario con email: {email}")
            usuario = db.query(Usuario).filter(Usuario.correo == email).first()
            
            if not usuario:
                logger.error(f"[ERROR] Usuario no encontrado: {email}")
                # Intentar buscar por usuario_id si está disponible
                if usuario_id:
                    logger.info(f"[DB] Intentando buscar por ID: {usuario_id}")
                    usuario = db.query(Usuario).filter(Usuario.id == int(usuario_id)).first()
                
                if not usuario:
                    raise ValueError(f"User not found: {email}")
            
            logger.info(f"[OK] Usuario encontrado: {usuario.nombre} (ID: {usuario.id})")
            
            # Buscar membresía
            logger.info(f"[DB] Buscando membresia ID: {membresia_id}")
            membresia = db.query(Membresia).filter(
                Membresia.id == int(membresia_id)
            ).first()
            
            if not membresia:
                logger.error(f"[ERROR] Membresia no encontrada: {membresia_id}")
                raise ValueError(f"Membership not found: {membresia_id}")
            
            logger.info(f"[OK] Membresia encontrada: {membresia.nombre}")
            logger.info(f"[MEMBERSHIP] Precio: ${membresia.precio} USD")
            logger.info(f"[MEMBERSHIP] Duracion: {membresia.duracion} dias")
            
            # Verificar pago duplicado
            logger.info(f"[DB] Verificando si el pago ya existe: {session['id']}")
            pago_existente = db.query(Pago).filter(
                Pago.referencia_pasarela == session['id']
            ).first()
            
            if pago_existente:
                logger.warning(f"[WARNING] Pago duplicado - ID: {pago_existente.id}")
                return JSONResponse({
                    "status": "duplicate",
                    "pago_id": pago_existente.id,
                    "message": "Payment already processed"
                })
            
            # Verificar si ya existe una suscripción activa para este usuario
            from repositories.suscripcion_repository import get_active_suscripcion_by_user_id
            logger.info(f"[DB] Verificando si el usuario ya tiene una suscripción activa...")
            suscripcion_activa_existente = get_active_suscripcion_by_user_id(db, usuario.id)
            
            if suscripcion_activa_existente:
                logger.info(f"[INFO] Usuario ya tiene suscripción activa (ID: {suscripcion_activa_existente.id})")
                logger.info(f"[INFO] Usando suscripción existente en lugar de crear una nueva")
                nueva_suscripcion = suscripcion_activa_existente
            else:
                # Crear suscripción
                logger.info("[DB] Creando nueva suscripcion...")
                fecha_inicio = datetime.utcnow()
                fecha_fin = fecha_inicio + timedelta(days=membresia.duracion)
                
                nueva_suscripcion = Suscripcion(
                    usuario_id=usuario.id,
                    membresia_id=membresia.id,
                    fecha_inicio=fecha_inicio,
                    fecha_fin=fecha_fin,
                    estado='activa'
                )
                db.add(nueva_suscripcion)
                db.flush()  # Obtener ID sin commit final
            
            logger.info(f"[OK] Suscripcion creada - ID: {nueva_suscripcion.id}")
            logger.info(f"[SUBSCRIPTION] Inicio: {fecha_inicio}")
            logger.info(f"[SUBSCRIPTION] Fin: {fecha_fin}")
            logger.info(f"[SUBSCRIPTION] Estado: activa")
            
            # Crear pago
            logger.info("[DB] Creando registro de pago...")
            amount_in_dollars = amount_total / 100  # Convertir centavos a dólares
            
            nuevo_pago = Pago(
                suscripcion_id=nueva_suscripcion.id,
                monto=amount_in_dollars,
                moneda=currency.upper(),
                metodo='card',
                estado='succeeded' if payment_status == 'paid' else 'pending',
                referencia_pasarela=session['id'],
                fecha_pago=datetime.utcnow()
            )
            db.add(nuevo_pago)
            
            # Commit final
            logger.info("[DB] Haciendo commit a la base de datos...")
            db.commit()
            db.refresh(nueva_suscripcion)
            db.refresh(nuevo_pago)
            
            logger.info(f"[OK] Pago registrado - ID: {nuevo_pago.id}")
            logger.info(f"[PAYMENT] Monto: ${nuevo_pago.monto} {nuevo_pago.moneda}")
            logger.info(f"[PAYMENT] Estado: {nuevo_pago.estado}")
            logger.info(f"[PAYMENT] Referencia: {nuevo_pago.referencia_pasarela}")
            logger.info("[SUCCESS] Proceso completado exitosamente!")
            logger.info("=" * 80)
            
            return JSONResponse({
                "status": "success",
                "suscripcion_id": nueva_suscripcion.id,
                "pago_id": nuevo_pago.id,
                "usuario_id": usuario.id,
                "membresia": membresia.nombre
            })
            
        except ValueError as ve:
            logger.error(f"[ERROR] Error de validacion: {str(ve)}")
            logger.error(f"[TRACEBACK] {traceback.format_exc()}")
            db.rollback()
            raise HTTPException(status_code=400, detail=str(ve))
            
        except Exception as e:
            logger.error(f"[ERROR] Error inesperado en checkout.session.completed")
            logger.error(f"[ERROR] Tipo: {type(e).__name__}")
            logger.error(f"[ERROR] Mensaje: {str(e)}")
            logger.error(f"[TRACEBACK] {traceback.format_exc()}")
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
    
    # Otros eventos
    elif event['type'] == 'payment_intent.succeeded':
        logger.info("[INFO] payment_intent.succeeded recibido (ignorado)")
    elif event['type'] == 'payment_intent.created':
        logger.info("[INFO] payment_intent.created recibido (ignorado)")
    elif event['type'] == 'charge.succeeded':
        logger.info("[INFO] charge.succeeded recibido (ignorado)")
    elif event['type'] == 'charge.updated':
        logger.info("[INFO] charge.updated recibido (ignorado)")
    else:
        logger.info(f"[INFO] Evento no manejado: {event['type']}")
    
    return JSONResponse({"status": "received"})