from fastapi import APIRouter, Depends, HTTPException
from schemas.delivery import delivery
from schemas.phone import somePhone as sp
from sqlalchemy.orm import Session
from sqlalchemy import text
from connection.config import get_db
from schemas.company import status
from models.phone import phoneRegistrastion
from models.delivery import deliveryRegistration
from models.bill import billRegistrastion
from models.reparation import reparationRegistration

router = APIRouter()


@router.get("/someDataPhone/{company}", response_model=list[sp])
async def someDataPhone(company:str,db: Session = Depends(get_db)):
    try:
        query = text("""
            SELECT p.phone_ref, p.brand_name, p.device, p.details, b.entry_date FROM phone as p 
            INNER JOIN bill AS b ON p.bill_number = b.bill_number
            INNER JOIN shift AS s ON b.ref_shift = s.ref_shift
            INNER JOIN worker AS w ON s.document = w.document
            INNER JOIN company AS c ON w.company = c.company_user
            WHERE c.company_user = :company AND p.repaired = 0;
        """)

        result = db.execute(query, {
            "company": company,  # Permite búsquedas parciales
            }).mappings().all() #Aquí obtenemos las filas como diccionarios

        if not result:
            raise HTTPException(status_code=404, detail="No hay dispositivos registrados")

        return result  # Ya no necesitas convertir manualmente

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.put("/repairphone/{phone_ref}/{ref_shift}/{bill_number}", response_model=status)
async def repairphone(phone_ref:str, ref_shift:str, bill_number:str, db:Session = Depends(get_db)):
    try:
        phone = db.query(phoneRegistrastion).filter(phoneRegistrastion.phone_ref == phone_ref).first()
        phone.repaired = True
        db.commit()
        db.refresh(phone)

        data = reparationRegistration(
            ref_shift= ref_shift,
            phone_ref= phone_ref,
            bill_number= bill_number
        )
        db.add(data)
        db.commit()
        db.refresh(data)
        return status(status="El Telefono ha sido reparado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/phoneBySearch/{company}/{phone_ref}", response_model=list[sp])
async def someDataPhone(phone_ref:str, company:str,db: Session = Depends(get_db)):
    try:
        query = text("""
            SELECT p.phone_ref, p.brand_name, p.device, p.details, b.entry_date FROM phone as p 
            INNER JOIN bill AS b ON p.bill_number = b.bill_number
            INNER JOIN shift AS s ON b.ref_shift = s.ref_shift
            INNER JOIN worker AS w ON s.document = w.document
            INNER JOIN company AS c ON w.company = c.company_user
            WHERE c.company_user = :company AND p.phone_ref LIKE :phone_ref AND p.repaired = 0;
        """)

        result = db.execute(query, {
            "company": company,
            "phone_ref": f"%{phone_ref}%"  # Permite búsquedas parciales
        }).mappings().all()

        if not result:
            raise HTTPException(status_code=404, detail="No hay dispositivos registrados")

        return result  # Ya no necesitas convertir manualmente

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/someDataPhoneDelivered/{company}", response_model=list[sp])
async def someDataPhone(company:str,db: Session = Depends(get_db)):
    try:
        query = text("""
            SELECT p.phone_ref, p.brand_name, p.device, p.details, b.entry_date FROM phone as p 
            INNER JOIN bill AS b ON p.bill_number = b.bill_number
            INNER JOIN shift AS s ON b.ref_shift = s.ref_shift
            INNER JOIN worker AS w ON s.document = w.document
            INNER JOIN company AS c ON w.company = c.company_user
            WHERE c.company_user = :company AND p.repaired = 1 AND p.delivered = 0;
        """)

        result = db.execute(query, {
            "company": company,  # Permite búsquedas parciales
            }).mappings().all() #Aquí obtenemos las filas como diccionarios

        if not result:
            raise HTTPException(status_code=404, detail="No hay dispositivos registrados")

        return result  # Ya no necesitas convertir manualmente

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))    

@router.put("/deliveredPhone/{phone_ref}/{bill_number}", response_model=status)
async def deliveredPhone(phone_ref:str,delivery:delivery,bill_number:str,db:Session = Depends(get_db)):
    try:
        phone = db.query(phoneRegistrastion).filter(phoneRegistrastion.phone_ref == phone_ref).first()
        phone.delivered = True
        db.commit()
        db.refresh(phone)

        bill = db.query(billRegistrastion).filter(billRegistrastion.bill_number == bill_number).first()
        bill.due -= delivery.sale
        bill.payment += delivery.sale
        db.commit()
        db.refresh(bill)

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
        return status(status="El Telefono ha sido Entregado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/phoneBySearchDelivered/{company}/{phone_ref}", response_model=list[sp])
async def someDataPhone(phone_ref:str,company:str,db: Session = Depends(get_db)):
    try:
        query = text("""
            SELECT p.phone_ref, p.brand_name, p.device, p.details, b.entry_date FROM phone as p 
            INNER JOIN bill AS b ON p.bill_number = b.bill_number
            INNER JOIN shift AS s ON b.ref_shift = s.ref_shift
            INNER JOIN worker AS w ON s.document = w.document
            INNER JOIN company AS c ON w.company = c.company_user
            WHERE c.company_user = :company AND p.phone_ref LIKE :phone_ref AND p.repaired = 1 and p.delivered = 0;
        """)

        result = db.execute(query, {
            "company": company,
            "phone_ref": f"%{phone_ref}%"  # Permite búsquedas parciales
        }).mappings().all()

        if not result:
            raise HTTPException(status_code=404, detail="No hay dispositivos registrados")

        return result  # Ya no necesitas convertir manualmente

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/getBillNumber/{phone_ref}")
async def getBillNumber(phone_ref:str,db: Session = Depends(get_db)):
    try:
        query = text("""
            SELECT bill_number FROM phone where phone_ref = :phone_ref
        """)

        result = db.execute(query, {"phone_ref": phone_ref}).mappings().all()

        if not result:
            raise HTTPException(status_code=404, detail="No hay dispositivos registrados")

        return result  # Ya no necesitas convertir manualmente

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


