from fastapi import APIRouter, HTTPException, Request, Depends, Query
from sqlalchemy.orm import Session
from connection.config import get_db
from models.subscription import SubscriptionRegistration
from services.bold_api import BoldAPI
import os
import json
import hmac
import hashlib
from datetime import datetime
import logging
import base64
from dateutil.relativedelta import relativedelta

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Obtener la clave secreta desde las variables de entorno
BOLD_SECRET_KEY = os.getenv("BOLD_SECRET_KEY", "")

# Inicializar el cliente de Bold API
bold_api = BoldAPI()

@router.post("/webhook/bold")
async def bold_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Endpoint para recibir notificaciones de eventos de pago de Bold.
    Este endpoint verifica la firma de la notificación y procesa el evento según su tipo.
    """
    try:
        # Obtener el cuerpo de la solicitud
        body = await request.json()
        logger.info(f"Webhook recibido: {json.dumps(body, indent=2)}")
        
        # Verificar la firma de la notificación
        signature = request.headers.get("x-bold-signature")
        if not signature:
            logger.error("Firma no encontrada en la solicitud")
            raise HTTPException(status_code=401, detail="Firma no encontrada")
        
        # Verificar la firma
        if not verify_signature(body, signature):
            logger.error("Firma inválida")
            raise HTTPException(status_code=401, detail="Firma inválida")
        
        # Extraer información relevante
        event_type = body.get("type")
        payment_data = body.get("data", {})
        payment_id = payment_data.get("payment_id")
        metadata = payment_data.get("metadata", {})
        reference = metadata.get("reference", "")
        
        logger.info(f"Evento recibido: {event_type}, Payment ID: {payment_id}, Referencia: {reference}")
        
        # Procesar el evento según su tipo
        if event_type == "SALE_APPROVED":
            # Pago aprobado
            await process_sale_approved(reference, payment_id, payment_data, db)
        elif event_type == "SALE_REJECTED":
            # Pago rechazado
            await process_sale_rejected(reference, payment_id, payment_data, db)
        elif event_type == "VOID_APPROVED":
            # Anulación aprobada
            await process_void_approved(reference, payment_id, payment_data, db)
        elif event_type == "VOID_REJECTED":
            # Anulación rechazada
            await process_void_rejected(reference, payment_id, payment_data, db)
        else:
            logger.warning(f"Tipo de evento no manejado: {event_type}")
        
        # Responder inmediatamente con 200 OK
        return {"status": "success", "message": "Evento recibido y procesado"}
    
    except Exception as e:
        logger.error(f"Error procesando webhook: {str(e)}")
        # Aún así respondemos con 200 para evitar reintentos de Bold
        return {"status": "error", "message": str(e)}

def verify_signature(payload, signature):
    """
    Verifica la firma de la notificación de Bold.
    
    Args:
        payload: El cuerpo de la notificación
        signature: La firma proporcionada en el encabezado
        
    Returns:
        bool: True si la firma es válida, False en caso contrario
    """
    try:
        # Convertir el payload a una cadena
        payload_str = json.dumps(payload)
        
        # Codificar el payload en Base64
        encoded = base64.b64encode(payload_str.encode("utf-8"))
        
        # Crear un hash HMAC con la clave secreta
        # En modo pruebas, la clave secreta es una cadena vacía
        secret_key = BOLD_SECRET_KEY if os.getenv("ENVIRONMENT", "development") == "production" else ""
        
        hashed = hmac.new(
            key=secret_key.encode(),
            msg=encoded,
            digestmod=hashlib.sha256
        ).hexdigest()
        
        # Comparar con la firma proporcionada
        return hmac.compare_digest(hashed, signature)
    
    except Exception as e:
        logger.error(f"Error verificando firma: {str(e)}")
        return False

async def process_sale_approved(reference, payment_id, payment_data, db):
    """
    Procesa un evento de venta aprobada.
    """
    try:
        logger.info(f"Iniciando procesamiento de venta aprobada para referencia: {reference}")
        
        parts = reference.split("-")
        if len(parts) < 3:
            logger.warning(f"Formato de referencia inválido: {reference}")
            return

        company = parts[0]
        plan = parts[1]
        amount_data = payment_data.get("amount", {})
        price = amount_data.get("total", 0)
        
        logger.info(f"Datos extraídos - Compañía: {company}, Plan: {plan}, Precio: {price}")

        date_start = datetime.now().date()
        payment_date = date_start + relativedelta(months=1, days=5)

        # Buscar la suscripción correspondiente
        subscription = (
            db.query(SubscriptionRegistration)
            .filter(SubscriptionRegistration.company == company)
            .first()
        )

        if subscription:
            logger.info(f"Actualizando suscripción existente para {company}")
            subscription.active = True
            subscription.date_start = date_start  # Fecha actual sin hora
            subscription.paymentDate = payment_date  # 1 mes después y 5 dias
            subscription.plan = plan
            subscription.price = price
            subscription.payment_id = payment_id
            subscription.payment_method = payment_data.get("payment_method", "")
            subscription.payment_status = "completed"
            db.commit()
            db.refresh(subscription)

    except Exception as e:
        logger.error(f"Error procesando venta aprobada: {str(e)}", exc_info=True)
        db.rollback()
        raise  # Re-lanza la excepción para que se registre en el webhook principal

async def process_sale_rejected(reference, payment_id, payment_data, db):
    """
    Procesa un evento de venta rechazada.
    
    Args:
        reference: Referencia del pago
        payment_id: ID del pago en Bold
        payment_data: Datos completos del pago
        db: Sesión de base de datos
    """
    try:
        # Extraer información de la referencia (formato: company-plan-payment_id)
        parts = reference.split("-")
        if len(parts) >= 3:
            company = parts[0]
            
            # Buscar la suscripción correspondiente
            subscription = (
                db.query(SubscriptionRegistration)
                .filter(SubscriptionRegistration.company == company)
                .first()
            )
            
            if subscription:
                # Actualizar el estado de pago
                subscription.payment_id = payment_id
                subscription.payment_method = payment_data.get("payment_method", "")
                subscription.payment_status = "rejected"
                
                db.commit()
                logger.info(f"Pago rechazado para {company}")
            else:
                logger.warning(f"No se encontró suscripción para {company}")
        else:
            logger.warning(f"Formato de referencia inválido: {reference}")
    
    except Exception as e:
        logger.error(f"Error procesando venta rechazada: {str(e)}")
        db.rollback()

async def process_void_approved(reference, payment_id, payment_data, db):
    """
    Procesa un evento de anulación aprobada.
    
    Args:
        reference: Referencia del pago
        payment_id: ID del pago en Bold
        payment_data: Datos completos del pago
        db: Sesión de base de datos
    """
    try:
        # Extraer información de la referencia (formato: company-plan-payment_id)
        parts = reference.split("-")
        if len(parts) >= 3:
            company = parts[0]
            
            # Buscar la suscripción correspondiente
            subscription = (
                db.query(SubscriptionRegistration)
                .filter(SubscriptionRegistration.company == company)
                .first()
            )
            
            if subscription:
                # Actualizar el estado de pago
                subscription.payment_status = "voided"
                
                db.commit()
                logger.info(f"Pago anulado para {company}")
            else:
                logger.warning(f"No se encontró suscripción para {company}")
        else:
            logger.warning(f"Formato de referencia inválido: {reference}")
    
    except Exception as e:
        logger.error(f"Error procesando anulación aprobada: {str(e)}")
        db.rollback()

async def process_void_rejected(reference, payment_id, payment_data, db):
    """
    Procesa un evento de anulación rechazada.
    
    Args:
        reference: Referencia del pago
        payment_id: ID del pago en Bold
        payment_data: Datos completos del pago
        db: Sesión de base de datos
    """
    try:
        # Extraer información de la referencia (formato: company-plan-payment_id)
        parts = reference.split("-")
        if len(parts) >= 3:
            company = parts[0]
            
            # Buscar la suscripción correspondiente
            subscription = (
                db.query(SubscriptionRegistration)
                .filter(SubscriptionRegistration.company == company)
                .first()
            )
            
            if subscription:
                # Actualizar el estado de pago
                subscription.payment_status = "void_rejected"
                
                db.commit()
                logger.info(f"Anulación rechazada para {company}")
            else:
                logger.warning(f"No se encontró suscripción para {company}")
        else:
            logger.warning(f"Formato de referencia inválido: {reference}")
    
    except Exception as e:
        logger.error(f"Error procesando anulación rechazada: {str(e)}")
        db.rollback()

@router.get("/webhook/bold/notification/{payment_id}")
async def get_bold_notification(
    payment_id: str,
    is_external_reference: bool = Query(False, description="Si es True, payment_id se trata como referencia externa"),
    db: Session = Depends(get_db)
):
    """
    Endpoint para consultar el estado de una notificación de Bold usando el servicio de fallback.
    
    Args:
        payment_id: ID de la transacción o referencia externa
        is_external_reference: Si es True, payment_id se trata como referencia externa
        db: Sesión de base de datos
        
    Returns:
        Dict: Respuesta de la API con las notificaciones
    """
    try:
        # Consultar la notificación usando el servicio de fallback
        response = bold_api.get_webhook_notification(payment_id, is_external_reference)
        
        # Procesar la notificación si existe
        if response.get("notifications") and len(response["notifications"]) > 0:
            notification = response["notifications"][0]  # Tomar la primera notificación
            
            # Extraer información relevante
            event_type = notification.get("type")
            payment_data = notification.get("data", {})
            metadata = payment_data.get("metadata", {})
            reference = metadata.get("reference", "")
            
            logger.info(f"Notificación encontrada: {event_type}, Payment ID: {payment_id}, Referencia: {reference}")
            
            # Procesar el evento según su tipo
            if event_type == "SALE_APPROVED":
                await process_sale_approved(reference, payment_id, payment_data, db)
            elif event_type == "SALE_REJECTED":
                await process_sale_rejected(reference, payment_id, payment_data, db)
            elif event_type == "VOID_APPROVED":
                await process_void_approved(reference, payment_id, payment_data, db)
            elif event_type == "VOID_REJECTED":
                await process_void_rejected(reference, payment_id, payment_data, db)
            else:
                logger.warning(f"Tipo de evento no manejado: {event_type}")
        
        return response
    
    except Exception as e:
        logger.error(f"Error consultando notificación de Bold: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 