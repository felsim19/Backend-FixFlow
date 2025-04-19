from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.company import status
from schemas.outflow import outflow, outflowExcel
from models.outflow import outflowRegistration
from connection.config import get_db
from sqlalchemy import text

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


@router.get("/allOutflowsCompany/{company}", response_model=list[outflowExcel])
async def allOutflowsCompany(company:str, db: Session = Depends(get_db)):
    try:
        # Consulta que incluye el filtro de la compañía y permite búsquedas parciales por número de factura
        query = text("""
            select o.ref_outflow, o.details, o.price from outflow 
            as o inner join shift as s on o.ref_shift = s.ref_shift     
            inner join premises as p on s.ref_premises = p.ref_premises where p.company = :company
        """)

        # Ejecutar la consulta con los parámetros proporcionados
        result = db.execute(query, {
            "company": company, # Permite búsquedas parciales
        }).mappings().all()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 


