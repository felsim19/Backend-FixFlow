from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from models.shift import shiftRegistration
from models.premises import premisesRegistration
from connection.config import get_db
from schemas.shift import shiftclose, someShift
from schemas.bill import someBill as bm, someDelivery as sd
from schemas.outflow import someOutflow as so

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
    

@router.put("/closeshift/{ref_shift}/{ref_premises}")
async def closeshift(ref_shift:str,ref_premises:int, shiftclose:shiftclose, db: Session = Depends(get_db)):
    try:
        shift = db.query(shiftRegistration).filter(shiftRegistration.ref_shift == ref_shift ).first()
        # Registrar la salida de inicio del turno
        now = datetime.now()
        shift.finish_time = now
        shift.total_gain = shiftclose.total_gain
        shift.total_received = shiftclose.total_received
        shift.total_outs = shiftclose.total_outs
        db.commit()
        db.refresh(shift)

        premise = db.query(premisesRegistration).filter(premisesRegistration.ref_premises == ref_premises).first()
        if not premise:
            raise HTTPException(status_code=404, detail="local no existe")
        premise.vault += shiftclose.vault
        db.commit() 
        db.refresh(premise) 

        return shift
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/someDataOfShift", response_model=list[someShift])
async def someDataBill(db: Session = Depends(get_db)):
    try:
        query = text("""
            SELECT ref_shift, document, date_shift 
            FROM shift
        """)

        result = db.execute(query).mappings().all()  # Aquí obtenemos las filas como diccionarios

        if not result:
            raise HTTPException(status_code=404, detail="No hay dispositivos registrados")

        return result  # Ya no necesitas convertir manualmente

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/allShiftCompany/{company}")
async def get_shift(company:str,db: Session = Depends(get_db)):
        query = text("""
            SELECT s.* 
            FROM shift as s inner join worker as w on s.id = w.id
            inner join company as c on w.company = c.company_user where c.company_user = :company 
            ORDER BY s.ref_shift DESC;
        """)

        result = db.execute(query, {"company": company}).mappings().all() # Aquí obtenemos las filas como diccionarios

        if not result:
            raise HTTPException(status_code=404, detail="No hay dispositivos registrados")

        return result  # Ya no necesitas convertir manualmente


@router.get("/shiftReceived/{ref_shift}", response_model=list[bm])
async def someDataBill(ref_shift:str, db: Session = Depends(get_db)):
    try:
        query = text("""
                SELECT b.bill_number, b.client_name, b.entry_date
                fROM bill as b inner join shift as s on 
                b.ref_shift = s.ref_shift where s.ref_shift = :ref_shift
        """)

        # Pasamos el parámetro a la consulta con bindparam para evitar SQL Injection
        result = db.execute(query, {"ref_shift": ref_shift}).mappings().all()

        if not result:
            raise HTTPException(status_code=404, detail="Factura no encontrada")

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/shiftRepaired/{ref_shift}", response_model=list[bm])
async def get_repaired_phones(ref_shift: str, db: Session = Depends(get_db)):
    try:
        query = text("""
            SELECT b.bill_number, b.client_name, b.entry_date
            FROM phone AS p
            INNER JOIN reparation AS r ON p.phone_ref = r.phone_ref
            INNER JOIN bill AS b ON r.bill_number = b.bill_number
            INNER JOIN shift AS s ON r.ref_shift = s.ref_shift
            WHERE s.ref_shift = :ref_shift AND p.repaired = 1;
        """)

        result = db.execute(query, {"ref_shift": ref_shift}).mappings().all()

        if not result:
            raise HTTPException(status_code=404, detail="No hay teléfonos reparados para este turno.")

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/shiftDelivery/{ref_shift}", response_model=list[bm])
async def get_repaired_phones(ref_shift: str, db: Session = Depends(get_db)):
    try:
        query = text("""
            SELECT b.bill_number, b.client_name, b.entry_date
            FROM phone AS p
            INNER JOIN reparation AS r ON p.phone_ref = r.phone_ref
            INNER JOIN bill AS b ON r.bill_number = b.bill_number
            INNER JOIN shift AS s ON r.ref_shift = s.ref_shift
            WHERE s.ref_shift = :ref_shift AND p.delivered  = 1;
        """)

        result = db.execute(query, {"ref_shift": ref_shift}).mappings().all()

        if not result:
            raise HTTPException(status_code=404, detail="No hay teléfonos reparados para este turno.")

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    



@router.get("/shiftSales/{ref_shift}", response_model=list[sd])
async def shiftSales(ref_shift:str, db: Session = Depends(get_db)):
    try:
        query = text("""
                SELECT d.product, d.sale
                fROM delivery as d inner join shift as s on 
                d.ref_shift = s.ref_shift where s.ref_shift = :ref_shift
        """)

        # Pasamos el parámetro a la consulta con bindparam para evitar SQL Injection
        result = db.execute(query, {"ref_shift": ref_shift}).mappings().all()

        if not result:
            raise HTTPException(status_code=404, detail="Factura no encontrada")

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/shiftOuts/{ref_shift}", response_model=list[so])
async def shiftOuts(ref_shift:str, db: Session = Depends(get_db)):
    try:
        query = text("""
                SELECT o.price, o.details
                fROM outflow as o inner join shift as s on 
                o.ref_shift = s.ref_shift where s.ref_shift = :ref_shift
        """)

        # Pasamos el parámetro a la consulta con bindparam para evitar SQL Injection
        result = db.execute(query, {"ref_shift": ref_shift}).mappings().all()

        if not result:
            raise HTTPException(status_code=404, detail="Factura no encontrada")

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/searchDateShift/{company}/{date_shift}", response_model=list[someShift])
async def someDataPhone(date_shift:str,company:str,db: Session = Depends(get_db)):
    try:
        query = text("""
            SELECT s.ref_shift, s.document, s.date_shift from shift as s 
            INNER JOIN worker AS w ON s.id = w.id
            INNER JOIN company AS c ON w.company = c.company_user
            WHERE c.company_user = :company AND s.date_shift = :date_shift;
        """)

        result = db.execute(query, {
            "company": company,
            "date_shift": f"{date_shift}"  # Permite búsquedas parciales
        }).mappings().all()

        if not result:
            raise HTTPException(status_code=404, detail="No hay dispositivos registrados")

        return result  # Ya no necesitas convertir manualmente

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/searchWname/{document}}", response_model=list[someShift])
async def someDataPhone(document:str,db: Session = Depends(get_db)):
    try:
        query = text("""
            SELECT s.ref_shift, s.document, s.date_shift from shift as s 
            INNER JOIN worker AS w ON s.id = w.id
            INNER JOIN company AS c ON w.company = c.company_user
            WHERE w.document = :document;
        """)

        result = db.execute(query, {
            "document": document,
        }).mappings().all()

        if not result:
            raise HTTPException(status_code=404, detail="No hay dispositivos registrados")

        return result  # Ya no necesitas convertir manualmente

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


