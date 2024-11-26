from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from models.shift import shiftRegistration
from connection.config import get_db
from schemas.shift import shiftclose, someShift

router = APIRouter()


@router.get("/shift/{ref_shift}")
async def get_Brands(ref_shift:str ,db: Session = Depends(get_db)):
    try:
        shift = db.query(shiftRegistration).filter(shiftRegistration.ref_shift == ref_shift ).first()
        if not shift:
            raise HTTPException(status_code=404, detail="ese turno no existe")
        return shift
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.put("/closeshift/{ref_shift}")
async def closeshift(ref_shift:str, shiftclose:shiftclose, db: Session = Depends(get_db)):
    try:
        shift = db.query(shiftRegistration).filter(shiftRegistration.ref_shift == ref_shift ).first()
        # Registrar la salida de inicio del turno
        now = datetime.now()
        shift.finish_time = now
        shift.total_gain = shiftclose.total_gain
        shift.total_received = shiftclose.total_received
        db.commit()
        db.refresh(shift)

        return shift
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/someDataOfShift", response_model=list[someShift])
async def someDataBill(db: Session = Depends(get_db)):
    try:
        query = text("""
            SELECT ref_shift, document, start_time 
            FROM shift
        """)

        result = db.execute(query).mappings().all()  # Aquí obtenemos las filas como diccionarios

        if not result:
            raise HTTPException(status_code=404, detail="No hay dispositivos registrados")

        return result  # Ya no necesitas convertir manualmente

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/allShift")
async def get_Devices(db: Session = Depends(get_db)):
    try:
        shift_list = db.query(shiftRegistration).all()  # Consulta sin filtro
        if not shift_list:
            raise HTTPException(status_code=404, detail="No hay dispositvos registrados")
        return shift_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))