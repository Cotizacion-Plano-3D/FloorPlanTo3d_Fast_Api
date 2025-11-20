from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import stripe
import logging
from database import get_db
from models.membresia import Membresia
from models.usuario import Usuario
from models.suscripcion import Suscripcion
from repositories.suscripcion_repository import get_active_suscripcion_by_user_id
from config import settings
from middleware.auth_middleware import get_current_user
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

# Configurar logging
logger = logging.getLogger(__name__)

# Configura tu clave secreta de Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

router = APIRouter(prefix="/api/stripe", tags=["stripe"])

def crear_suscripcion_manual_interna(db: Session, usuario_id: int, membresia_id: int):
    """
    Función helper para crear suscripción manualmente.
    Retorna la suscripción creada o None si ya existe una activa.
    """
    try:
        # Verificar si ya existe una suscripción activa
        suscripcion_activa = get_active_suscripcion_by_user_id(db, usuario_id)
        if suscripcion_activa:
            logger.warning(f"⚠️ Usuario {usuario_id} ya tiene una suscripción activa (ID: {suscripcion_activa.id})")
            return None
        
        # Verificar que la membresía existe
        membresia = db.query(Membresia).filter(Membresia.id == membresia_id).first()
        if not membresia:
            logger.error(f"❌ Membresía no encontrada: ID {membresia_id}")
            return None
        
        # Crear la suscripción
        nueva_suscripcion = Suscripcion(
            usuario_id=usuario_id,
            membresia_id=membresia_id,
            fecha_inicio=datetime.utcnow(),
            fecha_fin=datetime.utcnow() + timedelta(days=membresia.duracion),
            estado='activa'
        )
        
        db.add(nueva_suscripcion)
        db.commit()
        db.refresh(nueva_suscripcion)
        
        logger.info(f"✅ Suscripción manual creada - ID: {nueva_suscripcion.id}")
        logger.info(f"   Usuario: {usuario_id}, Membresía: {membresia_id}")
        logger.info(f"   Fecha inicio: {nueva_suscripcion.fecha_inicio}")
        logger.info(f"   Fecha fin: {nueva_suscripcion.fecha_fin}")
        
        return nueva_suscripcion
        
    except Exception as e:
        logger.error(f"❌ Error al crear suscripción manual: {str(e)}")
        logger.exception("Stack trace completo:")
        db.rollback()
        return None

class CheckoutSessionRequest(BaseModel):
    membresia_id: int

@router.post("/create-checkout-session")
async def create_checkout_session(
    req: CheckoutSessionRequest, 
    db=Depends(get_db), 
    current_user: Usuario = Depends(get_current_user)
):
    logger.info(f"🛒 Iniciando creación de sesión de checkout")
    logger.info(f"👤 Usuario: {current_user.correo} (ID: {current_user.id})")
    logger.info(f"🎫 Membresía solicitada: ID {req.membresia_id}")
    
    # Buscar membresía
    membresia = db.query(Membresia).filter(Membresia.id == req.membresia_id).first()
    
    if not membresia:
        logger.error(f"❌ Membresía no encontrada: ID {req.membresia_id}")
        raise HTTPException(status_code=404, detail="Membresía no encontrada")
    
    logger.info(f"✅ Membresía encontrada: {membresia.nombre}")
    logger.info(f"💰 Precio: ${membresia.precio} USD")
    logger.info(f"📅 Duración: {membresia.duracion} días")
    logger.info(f"📝 Descripción: {membresia.descripcion}")
    
    try:
        # Preparar datos para Stripe
        precio_en_centavos = int(membresia.precio * 100)
        logger.info(f"💵 Precio en centavos para Stripe: {precio_en_centavos}")
        
        # Crear sesión de Stripe
        logger.info("🔄 Llamando a Stripe API para crear sesión...")
        
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": membresia.nombre,
                        "description": membresia.descripcion
                    },
                    "unit_amount": precio_en_centavos,
                },
                "quantity": 1,
            }],
            mode="payment",
            customer_email=current_user.correo,
            metadata={
                "membresia_id": str(membresia.id),
                "membresia_nombre": membresia.nombre,
                "usuario_id": str(current_user.id),
                "usuario_email": current_user.correo
            },
            success_url=f"{settings.FRONTEND_URL}/dashboard?success=true&session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{settings.FRONTEND_URL}/dashboard?canceled=true",
        )
        
        logger.info(f"✅ Sesión de Stripe creada exitosamente")
        logger.info(f"🆔 Session ID: {session.id}")
        logger.info(f"🔗 Checkout URL: {session.url}")
        logger.info(f"📧 Email del cliente: {session.customer_email}")
        logger.info(f"💳 Método de pago: {session.payment_method_types}")
        logger.info(f"📊 Estado de pago: {session.payment_status}")
        logger.info(f"🎯 Success URL: {session.success_url}")
        logger.info(f"❌ Cancel URL: {session.cancel_url}")
        
        # Verificar metadata
        logger.info(f"📦 Metadata enviada:")
        for key, value in session.metadata.items():
            logger.info(f"  - {key}: {value}")
        
        # Crear suscripción manual después de crear la sesión de Stripe
        logger.info("🔧 Creando suscripción manual después de crear sesión de checkout...")
        suscripcion_creada = crear_suscripcion_manual_interna(
            db=db,
            usuario_id=current_user.id,
            membresia_id=membresia.id
        )
        
        if suscripcion_creada:
            logger.info(f"✅ Suscripción manual creada exitosamente (ID: {suscripcion_creada.id})")
        else:
            logger.warning("⚠️ No se pudo crear la suscripción manual (puede que ya exista una activa o hubo un error)")
        
        logger.info(f"🎉 Sesión lista para redirigir al usuario")
        
        return JSONResponse({
            "id": session.id, 
            "url": session.url,
            "status": "success",
            "membresia": membresia.nombre,
            "precio": float(membresia.precio),
            "suscripcion_creada": suscripcion_creada.id if suscripcion_creada else None
        })
        
    except stripe.error.CardError as e:
        logger.error(f"❌ Error de tarjeta Stripe: {str(e)}")
        logger.error(f"   Código: {e.code}")
        logger.error(f"   Mensaje: {e.user_message}")
        raise HTTPException(status_code=400, detail=f"Error de tarjeta: {e.user_message}")
        
    except stripe.error.RateLimitError as e:
        logger.error(f"❌ Rate limit excedido en Stripe: {str(e)}")
        raise HTTPException(status_code=429, detail="Demasiadas solicitudes, intente más tarde")
        
    except stripe.error.InvalidRequestError as e:
        logger.error(f"❌ Solicitud inválida a Stripe: {str(e)}")
        logger.error(f"   Parámetros enviados:")
        logger.error(f"   - Precio: {precio_en_centavos}")
        logger.error(f"   - Email: {current_user.correo}")
        logger.error(f"   - Membresía ID: {membresia.id}")
        raise HTTPException(status_code=400, detail=f"Solicitud inválida: {str(e)}")
        
    except stripe.error.AuthenticationError as e:
        logger.error(f"❌ Error de autenticación con Stripe: {str(e)}")
        logger.error(f"   Verifica STRIPE_SECRET_KEY en .env")
        raise HTTPException(status_code=401, detail="Error de autenticación con Stripe")
        
    except stripe.error.APIConnectionError as e:
        logger.error(f"❌ Error de conexión con API de Stripe: {str(e)}")
        raise HTTPException(status_code=503, detail="No se pudo conectar con Stripe")
        
    except stripe.error.StripeError as e:
        logger.error(f"❌ Error general de Stripe: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error de Stripe: {str(e)}")
        
    except Exception as e:
        logger.error(f"❌ Error inesperado: {str(e)}")
        logger.exception("Stack trace completo:")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")