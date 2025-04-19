from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from schemas.company import status
from schemas.delivery import delivery, deliveryExcel
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
    

@router.get("/allSalesPremises/{premises_id}", response_model=list[deliveryExcel])
async def allSalesPremises(premises_id:int, db: Session = Depends(get_db)):
    try:
        # Consulta que incluye el filtro de la compañía y permite búsquedas parciales por número de factura
        query = text("""
            select d.ref_delivery, d.product, d.sale, d.original_price, d.revenue_price, w.wname, s.date_shift from delivery 
            as d inner join shift as s on d.ref_shift = s.ref_shift 
            inner join worker as w on s.id = w.id where s.ref_premises = :premises_id
        """)

        # Ejecutar la consulta con los parámetros proporcionados
        result = db.execute(query, {
            "premises_id": premises_id, # Permite búsquedas parciales
        }).mappings().all()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 