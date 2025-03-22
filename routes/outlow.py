from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.company import status
from schemas.outflow import outflow
from models.outflow import outflowRegistration
from connection.config import get_db

router = APIRouter()

@router.post("/insertOutflow", response_model=status)
async def insertCompany(outflow:outflow,db:Session=Depends(get_db)):
    try:
        data = outflowRegistration(
            ref_shift = outflow.ref_shift,
            details = outflow.details,
            price = outflow.price
        )
        db.add(data)
        db.commit()
        db.refresh(data)
        return status(status="La venta ha sido registrada correctamente")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

