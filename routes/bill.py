from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from schemas.company import status
from schemas.bill import bill,someBill as sb, someBillRepair as sbr
from connection.config import get_db
from models.bill import billRegistrastion
from models.phone import phoneRegistrastion
from utils import generate_bill_number, internal_reference

router = APIRouter()

@router.post("/createBillwithPhones", response_model=status)
async def createBillwithPhones(bill: bill, db: Session = Depends(get_db)):
    if len(bill.phones) > 5:
        raise HTTPException(status_code=400, detail="No se puede registrar más de 5 dispositivos") 
    
    bill_number = generate_bill_number(db)
    newbill = billRegistrastion(
        bill_number=bill_number,
        total_price=bill.total_price,
        due=bill.due,
        client_name=bill.client_name,
        client_phone=bill.client_phone,
        payment=bill.payment,
        document=bill.document
    )
    db.add(newbill)
    db.commit()
    db.refresh(newbill)
    
    for phone in bill.phones:
        new_phone = phoneRegistrastion(
            phone_ref=internal_reference(db, bill_number),
            bill_number=newbill.bill_number,
            brand_name=phone.brand_name,  # Cambiado a brand_name
            device=phone.device,
            details=phone.details,
            individual_price=phone.individual_price
        )
        db.add(new_phone)
        db.commit()
        db.refresh(new_phone)
        
    return status(status="Factura y dispositivos registrados exitosamente")  

@router.get("/someDataOfBill", response_model=list[sb])
async def someDataBill(db: Session = Depends(get_db)):
    try:
        query = text("""
            SELECT bill_number, client_name, entry_date 
            FROM bill
        """)

        result = db.execute(query).mappings().all()  # Aquí obtenemos las filas como diccionarios

        if not result:
            raise HTTPException(status_code=404, detail="No hay dispositivos registrados")

        return result  # Ya no necesitas convertir manualmente

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/oneDataOfBill/{billNumber}", response_model=list[sb])
async def someDataBill(billNumber: str, db: Session = Depends(get_db)):
    try:
        query = text("""
            SELECT bill_number, client_name, entry_date 
            FROM bill
            WHERE bill_number = :bill_number
        """)

        # Pasamos el parámetro a la consulta con bindparam para evitar SQL Injection
        result = db.execute(query, {"bill_number": billNumber}).mappings().all()

        if not result:
            raise HTTPException(status_code=404, detail="Factura no encontrada")

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/billByClient/{client_name}", response_model=list[sb])
async def billByClient(client_name: str, db: Session = Depends(get_db)):
    try:
        query = text("""
            SELECT bill_number, client_name, entry_date 
            FROM bill
            WHERE client_name = :client_name
        """)

        # Pasamos el parámetro a la consulta con bindparam para evitar SQL Injection
        result = db.execute(query, {"client_name": client_name}).mappings().all()

        if not result:
            raise HTTPException(status_code=404, detail="Factura no encontrada")

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/billByDate/{entry_date}", response_model=list[sb])
async def billByDate(entry_date: str, db: Session = Depends(get_db)):
    try:
        query = text("""
            SELECT bill_number, client_name, entry_date 
            FROM bill
            WHERE entry_date = :entry_date
        """)

        # Pasamos el parámetro a la consulta con bindparam para evitar SQL Injection
        result = db.execute(query, {"entry_date": entry_date}).mappings().all()

        if not result:
            raise HTTPException(status_code=404, detail="Factura no encontrada")

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


    
@router.get("/bill/details/{bill_number}")
async def get_bill_and_phones(bill_number: str, db: Session = Depends(get_db)):
    try:
        bill = db.query(billRegistrastion).filter(billRegistrastion.bill_number == bill_number).first()
        if not bill:
            raise HTTPException(status_code=404, detail="Factura no encontrada")
        phones = db.query(phoneRegistrastion).filter(phoneRegistrastion.bill_number == bill_number).all()
        response = {
            "bill": bill,
            "phones": phones
        }
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/billCreatesWorker/{document}", response_model=list[sb])
async def someDataBill(document:str, db: Session = Depends(get_db)):
    try:
        query = text("""
            SELECT bill_number, client_name, entry_date 
            FROM bill
            WHERE document = :document
        """)

        # Pasamos el parámetro a la consulta con bindparam para evitar SQL Injection
        result = db.execute(query, {"document": document}).mappings().all()

        if not result:
            raise HTTPException(status_code=404, detail="Factura no encontrada")

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/billRepairWorker/{document}", response_model=list[sbr])
async def someDataBill(document:str, db: Session = Depends(get_db)):
    try:
        query = text("""
            SELECT b.bill_number, b.client_name, p.phone_ref fROM phone as p inner join bill as b
            on p.bill_number = b.bill_number where p.repaired = 1 and b.document = :document
        """)

        # Pasamos el parámetro a la consulta con bindparam para evitar SQL Injection
        result = db.execute(query, {"document": document}).mappings().all()

        if not result:
            raise HTTPException(status_code=404, detail="Factura no encontrada")

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/billDeliveredWorker/{document}", response_model=list[sbr])
async def someDataBill(document:str, db: Session = Depends(get_db)):
    try:
        query = text("""
            SELECT b.bill_number, b.client_name, p.phone_ref fROM phone as p inner join bill as b
            on p.bill_number = b.bill_number where p.delivered = 1 and b.document = :document
        """)

        # Pasamos el parámetro a la consulta con bindparam para evitar SQL Injection
        result = db.execute(query, {"document": document}).mappings().all()

        if not result:
            raise HTTPException(status_code=404, detail="Factura no encontrada")

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))