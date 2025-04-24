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


@router.get("/allOutflowsPremises/{premises_id}", response_model=list[outflowExcel])
async def allOutflowsPremises(premises_id:int, db: Session = Depends(get_db)):
    try:
        # Consulta que incluye el filtro de la compañía y permite búsquedas parciales por número de factura
        query = text("""
            select o.ref_outflow, o.details, o.price, w.wname, s.date_shift from outflow 
            as o inner join shift as s on o.ref_shift = s.ref_shift 
            inner join worker as w on s.id = w.id where s.ref_premises = :premises_id
            ORDER BY	            
            SUBSTRING_INDEX(o.ref_outflow, '_', 1) DESC, 
            CAST(SUBSTRING_INDEX(o.ref_outflow, '_', -1) AS UNSIGNED) DESC;
        """)

        # Ejecutar la consulta con los parámetros proporcionados
        result = db.execute(query, {
            "premises_id": premises_id, # Permite búsquedas parciales
        }).mappings().all()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 


