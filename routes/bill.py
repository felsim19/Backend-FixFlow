from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from schemas.company import status
from schemas.bill import bill,someBill as sb, someBillRepair as sbr, billRepairPhone as brp
from connection.config import get_db
from models.bill import billRegistrastion
from models.phone import phoneRegistrastion
from utils import generate_bill_number, internal_reference

router = APIRouter()

@router.post("/createBillwithPhones/{company}", response_model=status)
async def createBillwithPhones(company:str, bill: bill, db: Session = Depends(get_db)):
    if len(bill.phones) > 5:
        raise HTTPException(status_code=400, detail="No se puede registrar más de 5 dispositivos") 
    
    bill_number = generate_bill_number(db, company)
    newbill = billRegistrastion(
        bill_number=bill_number,
        total_price=bill.total_price,
        due=bill.due,
        client_name=bill.client_name,
        client_phone=bill.client_phone,
        payment=bill.payment,
        wname=bill.wname,
        ref_shift = bill.ref_shift
    )
    db.add(newbill)
    db.commit()
    db.refresh(newbill)
    
    for phone in bill.phones:
        new_phone = phoneRegistrastion(
            phone_ref=internal_reference(db, bill_number),
            bill_number=newbill.bill_number,
            brand_name=phone.brand_name,
            brand_id=phone.brand_id,  
            device=phone.device,
            details=phone.details,
            individual_price=phone.individual_price
        )
        db.add(new_phone)
        db.commit()
        db.refresh(new_phone)
        
    return status(status="Factura y dispositivos registrados exitosamente")  

@router.get("/someDataOfBill/{company}", response_model=list[sb])
async def someDataBill(company:str,db: Session = Depends(get_db)):
    try:
    
        query = text("""
            SELECT b.bill_number, b.client_name, b.entry_date 
            FROM bill as b inner join shift as s on b.ref_shift = s.ref_shift
            inner join worker as w on s.document = w.document inner join 
            company as c on w.company = c.company_user where c.company_user = :company;
        """)

        result = db.execute(query, {"company": company}).mappings().all() # Aquí obtenemos las filas como diccionarios

        if not result:
            raise HTTPException(status_code=404, detail="No hay dispositivos registrados")

        return result  # Ya no necesitas convertir manualmente

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/searchBillsByNumber/{company}/{billNumber}", response_model=list[sb])
async def oneDataBill(company: str, billNumber: str, db: Session = Depends(get_db)):
    try:
        # Consulta que incluye el filtro de la compañía y permite búsquedas parciales por número de factura
        query = text("""
            SELECT b.bill_number, b.client_name, b.entry_date 
            FROM bill AS b
            INNER JOIN shift AS s ON b.ref_shift = s.ref_shift
            INNER JOIN worker AS w ON s.document = w.document
            INNER JOIN company AS c ON w.company = c.company_user
            WHERE c.company_user = :company AND b.bill_number LIKE :bill_number
        """)

        # Ejecutar la consulta con los parámetros proporcionados
        result = db.execute(query, {
            "company": company,
            "bill_number": f"%{billNumber}%"  # Permite búsquedas parciales
        }).mappings().all()

        # Manejo de resultado vacío
        if not result:
            raise HTTPException(status_code=404, detail="Factura no encontrada")

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/searchBillsByName/{company}/{client_name}", response_model=list[sb])
async def oneDataBill(company: str, client_name: str, db: Session = Depends(get_db)):
    try:
        # Consulta que incluye el filtro de la compañía y permite búsquedas parciales por número de factura
        query = text("""
            SELECT b.bill_number, b.client_name, b.entry_date 
            FROM bill AS b
            INNER JOIN shift AS s ON b.ref_shift = s.ref_shift
            INNER JOIN worker AS w ON s.document = w.document
            INNER JOIN company AS c ON w.company = c.company_user
            WHERE c.company_user = :company AND b.client_name LIKE :client_name
        """)

        # Ejecutar la consulta con los parámetros proporcionados
        result = db.execute(query, {
            "company": company,
            "client_name": f"%{client_name}%"  # Permite búsquedas parciales
        }).mappings().all()

        # Manejo de resultado vacío
        if not result:
            raise HTTPException(status_code=404, detail="Factura no encontrada")

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/searchBillsByDate/{company}/{entry_date}", response_model=list[sb])
async def oneDataBill(company: str, entry_date: str, db: Session = Depends(get_db)):
    try:
        # Consulta que incluye el filtro de la compañía y permite búsquedas parciales por número de factura
        query = text("""
            SELECT b.bill_number, b.client_name, b.entry_date 
            FROM bill AS b
            INNER JOIN shift AS s ON b.ref_shift = s.ref_shift
            INNER JOIN worker AS w ON s.document = w.document
            INNER JOIN company AS c ON w.company = c.company_user
            WHERE c.company_user = :company AND b.entry_date LIKE :entry_date
        """)

        # Ejecutar la consulta con los parámetros proporcionados
        result = db.execute(query, {
            "company": company,
            "entry_date": f"%{entry_date}%"  # Permite búsquedas parciales
        }).mappings().all()

        # Manejo de resultado vacío
        if not result:
            raise HTTPException(status_code=404, detail="Factura no encontrada")

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/billRepairPhone/{phone_ref}", response_model=list[brp])
async def someDataBill(phone_ref: str, db: Session = Depends(get_db)):
    try:
        query = text("""
            SELECT b.due, b.client_name, b.payment, b.bill_number 
            FROM bill AS b
            INNER JOIN phone AS p ON b.bill_number = p.bill_number 
            WHERE p.phone_ref = :phone_ref;
        """)

        # Ejecuta la consulta y obtiene los resultados
        result = db.execute(query, {"phone_ref": phone_ref}).mappings().all()

        if not result:
            raise HTTPException(status_code=404, detail="Factura no encontrada")

        # Retorna directamente los resultados para que FastAPI los valide
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bill/details/{bill_number}")
async def get_bill_and_phones(bill_number: str, db: Session = Depends(get_db)):
    try:
        bill = db.query(billRegistrastion).filter(billRegistrastion.bill_number == bill_number).first()
        if not bill:
            raise HTTPException(status_code=404, detail="Factura no encontrada")
        phone = db.query(phoneRegistrastion).filter(phoneRegistrastion.bill_number == bill_number).all()
        response = {
            "bill": bill,
            "phones": phone
        }
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/billCreatesWorker/{document}", response_model=list[sb])
async def someDataBill(document:str, db: Session = Depends(get_db)):
    try:
        query = text("""
                SELECT b.bill_number, b.client_name, b.entry_date fROM bill as b
                inner join shift as s on b.ref_shift = s.ref_shift
                where s.document = :document
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
            SELECT DISTINCT b.bill_number, b.client_name, p.phone_ref fROM phone as p inner join bill as b
            on p.bill_number = b.bill_number inner join shift as s on b.ref_shift = s.ref_shift
            where p.repaired = 1 and s.document = :document
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
                on p.bill_number = b.bill_number inner join shift as s on b.ref_shift = s.ref_shift
                where p.delivered = 1 and s.document = :document
        """)    

        # Pasamos el parámetro a la consulta con bindparam para evitar SQL Injection
        result = db.execute(query, {"document": document}).mappings().all()

        if not result:
            raise HTTPException(status_code=404, detail="Factura no encontrada")

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/getnumberPhones/{bill_number}")
async def getPricePhone(bill_number:str,db: Session = Depends(get_db)):
    try:
        query = text("""
            SELECT 
            COUNT(*) AS numberphones,
            SUM(delivered) AS delivered_count
            FROM phone
            WHERE bill_number = :bill_number
            GROUP BY bill_number;
        """)

        result = db.execute(query, {"bill_number": bill_number}).mappings().all()

        if not result:
            raise HTTPException(status_code=404, detail="No hay dispositivos registrados")

        return result  # Ya no necesitas convertir manualmente

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))