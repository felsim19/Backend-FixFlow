from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.company import status
from schemas.delivery import delivery
from models.delivery import deliveryRegistration
from connection.config import get_db

router = APIRouter()

@router.post("/insertdelivery", response_model=status)
async def insertCompany(delivery:delivery,db:Session=Depends(get_db)):
    try:
        data = deliveryRegistration(
            ref_shift = delivery.ref_shift,
            product = delivery.product,
            sale = delivery.sale,
            original_price = delivery.original_price,
            revenue_price = delivery.revenue_price
        )
        db.add(data)
        db.commit()
        db.refresh(data)
        return status(status="La venta ha sido registrada correctamente")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))