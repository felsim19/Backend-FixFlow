# Integración con Bold para Pagos

Este documento describe cómo configurar y utilizar la integración con Bold para procesar pagos en la aplicación FixFlow.

## Configuración del Webhook

Para recibir notificaciones de eventos de pago de Bold, debes configurar un webhook en el Panel de Comercios de Bold. Sigue estos pasos:

1. Inicia sesión en el [Panel de Comercios de Bold](https://merchant.bold.co)
2. Navega a la sección de **Integraciones**
3. Busca la opción **Webhooks** o **Notificaciones**
4. Haz clic en **Agregar Webhook** o **Configurar Webhook**
5. Ingresa la URL de tu webhook: `https://tu-dominio.com/webhook/bold`
6. Selecciona los eventos que deseas recibir:
   - SALE_APPROVED (Venta aprobada)
   - SALE_REJECTED (Venta rechazada)
   - VOID_APPROVED (Anulación aprobada)
   - VOID_REJECTED (Anulación rechazada)
7. Guarda la configuración

## Variables de Entorno

Asegúrate de tener configuradas las siguientes variables de entorno en tu archivo `.env`:

```
BOLD_API_KEY=tu_api_key
BOLD_SECRET_KEY=tu_secret_key
BOLD_MERCHANT_ID=tu_merchant_id
BOLD_WEBHOOK_URL=https://tu-dominio.com/webhook/bold
FRONTEND_URL=https://tu-frontend-url/
```

## Flujo de Pago

1. El usuario selecciona un plan de suscripción
2. El sistema genera un ID de pago único
3. Se crea un botón de pago en Bold con la referencia del usuario
4. El usuario completa el pago en la interfaz de Bold
5. Bold envía una notificación al webhook con el resultado del pago
6. El sistema actualiza el estado de la suscripción según la notificación

## Pruebas Locales

Para probar la integración localmente, puedes usar herramientas como ngrok para exponer tu servidor local a Internet:

1. Instala ngrok: `npm install -g ngrok` o descárgalo de [ngrok.com](https://ngrok.com)
2. Inicia tu servidor FastAPI: `uvicorn main:app --reload`
3. Expón tu servidor: `ngrok http 8000`
4. Copia la URL HTTPS generada por ngrok
5. Actualiza la variable `BOLD_WEBHOOK_URL` en tu archivo `.env`
6. Configura el webhook en el Panel de Comercios de Bold con la nueva URL

## Solución de Problemas

- **Error 422**: Verifica que los parámetros enviados al endpoint `/subscription/hash` sean correctos
- **Error de firma**: Asegúrate de que la variable `BOLD_SECRET_KEY` esté correctamente configurada
- **No se reciben notificaciones**: Verifica que la URL del webhook sea accesible desde Internet y que esté correctamente configurada en Bold

## Recursos Adicionales

- [Documentación de Bold](https://docs.bold.co)
- [Guía de Integración de Bold](https://docs.bold.co/integration-guide)
- [API de Bold](https://docs.bold.co/api-reference) 