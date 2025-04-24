import os
import requests
import logging
from typing import Dict, List, Optional, Union

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BoldAPI:
    """
    Cliente para interactuar con la API de Bold.
    """
    
    def __init__(self):
        self.api_key = os.getenv("BOLD_API_KEY", "")
        self.base_url = "https://integrations.api.bold.co"
        
        if not self.api_key:
            logger.warning("BOLD_API_KEY no está configurada en las variables de entorno")
    
    def get_webhook_notification(self, payment_id: str, is_external_reference: bool = False) -> Dict:
        """
        Consulta la notificación de una transacción usando el servicio de fallback.
        
        Args:
            payment_id: ID de la transacción o referencia externa
            is_external_reference: Si True, payment_id se trata como referencia externa
            
        Returns:
            Dict: Respuesta de la API con las notificaciones
        """
        try:
            # Construir la URL
            url = f"{self.base_url}/payments/webhook/notifications/{payment_id}"
            
            # Agregar parámetro de referencia externa si es necesario
            params = {}
            if is_external_reference:
                params["is_external_reference"] = "true"
            
            # Configurar headers
            headers = {
                "Authorization": f"x-api-key {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Realizar la solicitud
            response = requests.get(url, params=params, headers=headers)
            
            # Verificar si la solicitud fue exitosa
            response.raise_for_status()
            
            # Devolver la respuesta como JSON
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al consultar notificación de Bold: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Código de estado: {e.response.status_code}")
                logger.error(f"Respuesta: {e.response.text}")
            raise 