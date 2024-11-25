from fastapi import APIRouter, Depends, HTTPException
from schemas.phone import somePhone as sp
from sqlalchemy.orm import Session
from sqlalchemy import text
from connection.config import get_db
from schemas.company import status
from models.phone import phoneRegistrastion

router = APIRouter()


@router.get("/someDataPhone", response_model=list[sp])
async def someDataPhone(db: Session = Depends(get_db)):
    try:
        query = text("""
            SELECT p.phone_ref, p.brand_name, p.device, p.details, b.entry_date FROM phone as p inner join bill as b
            on p.bill_number = b.bill_number where p.repaired = 0
        """)

        result = db.execute(query).mappings().all()  # Aquí obtenemos las filas como diccionarios

        if not result:
            raise HTTPException(status_code=404, detail="No hay dispositivos registrados")

        return result  # Ya no necesitas convertir manualmente

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


@router.put("/repairphone/{phone_ref}", response_model=status)
async def repairphone(phone_ref:str,db:Session = Depends(get_db)):
    try:
        phone = db.query(phoneRegistrastion).filter(phoneRegistrastion.phone_ref == phone_ref).first()
        phone.repaired = True
        db.commit()
        db.refresh(phone)
        return status(status="El Telefono ha sido reparado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/phoneBySearch/{phone_ref}", response_model=list[sp])
async def someDataPhone(phone_ref:str,db: Session = Depends(get_db)):
    try:
        query = text("""
            SELECT p.phone_ref, p.brand_name, p.device, p.details, b.entry_date FROM phone as p inner join bill as b
            on p.bill_number = b.bill_number where p.phone_ref = :phone_ref
        """)

        result = db.execute(query, {"phone_ref": phone_ref}).mappings().all()

        if not result:
            raise HTTPException(status_code=404, detail="No hay dispositivos registrados")

        return result  # Ya no necesitas convertir manualmente

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/someDataPhoneDelivered", response_model=list[sp])
async def someDataPhone(db: Session = Depends(get_db)):
    try:
        query = text("""
            SELECT p.phone_ref, p.brand_name, p.device, p.details, b.entry_date FROM phone as p inner join bill as b
            on p.bill_number = b.bill_number where p.repaired = 1 and p.delivered = 0
        """)

        result = db.execute(query).mappings().all()  # Aquí obtenemos las filas como diccionarios

        if not result:
            raise HTTPException(status_code=404, detail="No hay dispositivos registrados")

        return result  # Ya no necesitas convertir manualmente

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.put("/deliveredPhone/{phone_ref}", response_model=status)
async def deliveredPhone(phone_ref:str,db:Session = Depends(get_db)):
    try:
        phone = db.query(phoneRegistrastion).filter(phoneRegistrastion.phone_ref == phone_ref).first()
        phone.delivered = True
        db.commit()
        db.refresh(phone)
        return status(status="El Telefono ha sido Entregado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


@router.get("/phoneBySearchDelivered/{phone_ref}", response_model=list[sp])
async def someDataPhone(phone_ref:str,db: Session = Depends(get_db)):
    try:
        query = text("""
            SELECT p.phone_ref, p.brand_name, p.device, p.details, b.entry_date FROM phone as p inner join bill as b
            on p.bill_number = b.bill_number where p.phone_ref = :phone_ref
        """)

        result = db.execute(query, {"phone_ref": phone_ref}).mappings().all()

        if not result:
            raise HTTPException(status_code=404, detail="No hay dispositivos registrados")

        return result  # Ya no necesitas convertir manualmente

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    


