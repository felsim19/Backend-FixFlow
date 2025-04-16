from fastapi import APIRouter, HTTPException
import requests

router = APIRouter()

BOLD_API_KEY = "X5n7An82U_1zF2ml_BmW_ggSwzeVvtBQlhiin1aALWs"
BOLD_API_URL = "https://api.bold.co/online/link/v1"


@router.get("/paymentLink")
def crear_link_pago():
    headers = {
        "Authorization": f"Bearer {BOLD_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "amount": 20000,
        "currency": "COP",
        "description": "Suscripción mensual FixFlow",
        "callback_url": "localhost:5173/"
    }
    response = requests.post(BOLD_API_URL, json=data, headers=headers)
    if response.status_code == 201:
        return response.json()
    else:
        raise HTTPException(status_code=400, detail="Error al crear el link de pago")
