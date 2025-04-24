from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from schemas.company import status
from schemas.worker import worker, statusworker, workerlogin as wl, workerByPremise as wbp
from models.company import companyRegistration
from models.worker import workerRegistration
from models.shift import shiftRegistration
from connection.config import get_db
from utils import generate_shift_reference, get_words_worker
import bcrypt

router = APIRouter()


@router.post("/insertWorker/{nameCompany}", response_model=status)
async def insertWorker(nameCompany:str,worker:worker, db:Session=Depends(get_db)):
    try:
        company = db.query(companyRegistration).filter(companyRegistration.company_user == worker.company).first()
        if not company:
            raise HTTPException(status_code=404, detail="Compañia no existe")
        
        # verificar si el primer trabajador de la compañia
        workers_count = db.query(workerRegistration).filter(workerRegistration.company == worker.company).count()
        assigned_role = worker.wrole
        if workers_count == 0 and assigned_role != "Gerente":
            raise HTTPException(status_code=401, detail="usted al ser el primer empleado tendra un rol de gerente")
        elif workers_count == 0 and assigned_role == "Gerente":
            assigned_role
        elif workers_count != 0 and assigned_role == "Gerente":
            raise HTTPException(status_code=401, detail="Solo puede haber un gerente por empresa")
        else:
            assigned_role 
            
        
        encryption = bcrypt.hashpw(worker.password.encode('utf-8'), bcrypt.gensalt())
        
        new_worker = workerRegistration(
            id = get_words_worker(nameCompany, worker.document),
            wname = worker.wname,
            password = encryption.decode('utf-8'),
            document = worker.document,
            company = worker.company,
            wrole = assigned_role,
            active = True
        )
        
        id = db.query(workerRegistration).filter(workerRegistration.id == new_worker.id).first()
        if id:  
            raise HTTPException(status_code=401, detail="El documento ya existe.")
        
        db.add(new_worker)
        db.commit()
        db.refresh(new_worker)
        return status(status="Trabajador registrado exitosamente", msg="registro exitoso")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/company/{company_id}/count")
async def getWorkerCount(company_id:str, db:Session=Depends(get_db)): 
    try:
        count = db.query(workerRegistration).filter(workerRegistration.company == company_id).count()
        return {"count" : count }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/workerDateEntry/{id}")
async def getWorkerDateEntry(id:str, db:Session=Depends(get_db)): 
    try:
        worker = db.query(workerRegistration).filter(workerRegistration.id == id).first()
        return {"Date" : worker.dateEntry }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/collaborators/{company_id}/workers")
async def get_collaborators( company_id:str, db:Session = Depends(get_db)):
    try:
        clb_list = db.query(workerRegistration).filter(workerRegistration.company == company_id).all()
        return clb_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/workersByPremise/{premise_id}/{company_id}", response_model=list[wbp])
async def get_workers_by_premise(premise_id:int, company_id:str, db:Session = Depends(get_db)):
    try:
        query = text("""
            SELECT DISTINCT w.wname 
            FROM shift AS s
            INNER JOIN worker AS w ON s.id = w.id
            INNER JOIN premises AS p ON s.ref_premises = p.ref_premises
            INNER JOIN company AS c ON w.company = c.company_user
            WHERE c.company_user = :company AND s.ref_premises = :premises;
        """)

        result = db.execute(query, {"company": company_id, "premises": premise_id   }).mappings().all()  # Aquí obtenemos las filas como diccionarios

        if not result:
            raise HTTPException(status_code=404, detail="No hay dispositivos registrados")

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 

@router.get("/workerTotalShift/{id}")
async def get_worker_stats(id: str, db: Session = Depends(get_db)):
    try:
        # Primero verificar si el trabajador existe
        worker_exists = db.query(workerRegistration).filter(workerRegistration.id == id).first()
        if not worker_exists:
            raise HTTPException(status_code=404, detail="Trabajador no encontrado")
        
        # Contar los turnos del trabajador en el local específico
        shift_count = db.query(shiftRegistration).filter(
            shiftRegistration.id == id
        ).count()
        
        return {"count": shift_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/loginWorker/{company_id}", response_model=statusworker)
async def loginworker(company_id: str, worker_user: wl, db: Session = Depends(get_db)):
    try:
        # Buscar al trabajador en la base de datos
        db_worker = db.query(workerRegistration).filter(
            workerRegistration.id == get_words_worker(company_id, worker_user.document),
            workerRegistration.company == company_id
        ).first()

        # Validar que el trabajador exista
        if db_worker is None:
            raise HTTPException(status_code=400, detail="Documento no registrado.")
        
        if db_worker.active == False:
            raise HTTPException(status_code=401, detail="Trabajador inactivo")

        # Validar la contraseña
        if not bcrypt.checkpw(worker_user.password.encode('utf-8'), db_worker.password.encode('utf-8')):
            raise HTTPException(status_code=401, detail="Contraseña Incorrecta")

        # Registrar la hora de inicio del turno
        now = datetime.now()
        new_shift = shiftRegistration(
            id=get_words_worker(company_id, worker_user.document),
            start_time=now,
            ref_shift=generate_shift_reference(db),
            ref_premises=worker_user.premise_id
        )
        db.add(new_shift)
        db.commit()

        return {
            "status": "Inicio de sesión exitoso",
            "role": db_worker.wrole,
            "wname": db_worker.wname,
            "shift": new_shift.ref_shift,
            "id": db_worker.id,
            "document": db_worker.document
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/inactiveCollaborators/{company_id}/{document}/{documentActive}", response_model=status)
async def delete_collaborators(company_id:str,document:str, documentActive:str, db:Session = Depends(get_db)):
    try:
        worker = db.query(workerRegistration).filter(
            workerRegistration.company == company_id,
            workerRegistration.document == document
            ).first()
        
        if worker is None:
                raise HTTPException(status_code=404,detail="Trabajador no encontrado")
        
        if worker.wrole == "Gerente":
            raise HTTPException(status_code=401, detail="No se puede descativar el gerente de la empresa")
        
        if worker.document == documentActive:
            raise HTTPException(status_code=401, detail="No se puede descativar el trabajador que actualmente esta una sesion activa")
            
        worker.active = False
        db.commit()
        db.refresh(worker)
        return status(status="trabajador inactivado exitosamente")  
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/reactiveCollaborators/{company_id}/{document}", response_model=status)
async def delete_collaborators(company_id:str,document:str, db:Session = Depends(get_db)):
    try:
        worker = db.query(workerRegistration).filter(
            workerRegistration.company == company_id,
            workerRegistration.document == document
            ).first()
        
        if worker is None:
                raise HTTPException(status_code=404,detail="Trabajador No Encontrado")
            
        worker.active = True
        db.commit()
        db.refresh(worker)
        return status(status="trabajador Reactivado Exitosamente")  
    except Exception as e:  
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/worker/{workerDocument}/{company}")
async def get_worker_wname(workerDocument:str, company:str, db:Session=Depends(get_db)): 
    try:
        worker = db.query(workerRegistration).filter(workerRegistration.document == workerDocument, 
                                                     workerRegistration.company == company).first()
        
        if worker is None:
            raise HTTPException(status_code=404, detail="Trabajador no encontrado")
            
        return {"wname" : worker.wname }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/workerExcel/shifts/{document}/{loggedCompany}")       
async def get_worker_excel_shifts(document:str, loggedCompany:str, db:Session=Depends(get_db)):
    try:
        query = text("""
            SELECT s.*
            FROM shift AS s
            INNER JOIN worker AS w ON s.id = w.id
            INNER JOIN company AS c ON w.company = c.company_user
            WHERE w.document = :document AND c.company_user = :company
            ORDER BY 
            SUBSTRING_INDEX(s.ref_shift, '_', 1) DESC, 
            CAST(SUBSTRING_INDEX(s.ref_shift, '_', -1) AS UNSIGNED) DESC;   
        """)

        result = db.execute(query, {"document": document, "company": loggedCompany}).mappings().all() # Aquí obtenemos las filas como diccionarios

        if not result:
            raise HTTPException(status_code=404, detail="No hay dispositivos registrados")

        return result  # Ya no necesitas convertir manualmente
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workerExcel/bills/{document}/{loggedCompany}")       
async def get_worker_excel_bills(document:str, loggedCompany:str, db:Session=Depends(get_db)):
    try:
        query = text("""
            SELECT b.bill_number, b.client_name, b.entry_date, b.wname, b.client_phone, b.total_price
            FROM bill as b inner join shift as s on b.ref_shift = s.ref_shift
            inner join worker as w on s.id = w.id 
            inner join premises as p on s.ref_premises = p.ref_premises
            where w.document = :document AND p.company = :company
            ORDER BY	            
            SUBSTRING_INDEX(b.bill_number, '_', 1) DESC, 
            CAST(SUBSTRING_INDEX(b.bill_number, '_', -1) AS UNSIGNED) DESC;
        """)

        result = db.execute(query, {"document": document, "company": loggedCompany}).mappings().all() # Aquí obtenemos las filas como diccionarios

        if not result:
            raise HTTPException(status_code=404, detail="No hay dispositivos registrados")

        return result  # Ya no necesitas convertir manualmente
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workerExcel/sales/{document}/{loggedCompany}")       
async def get_worker_excel_sales(document:str, loggedCompany:str, db:Session=Depends(get_db)):
    try:
        query = text("""
            select d.ref_delivery, d.product, d.sale, d.original_price, d.revenue_price, w.wname, s.date_shift from delivery 
            as d inner join shift as s on d.ref_shift = s.ref_shift  
            inner join premises as p on s.ref_premises = p.ref_premises
            inner join worker as w on s.id = w.id where w.document = :document AND p.company = :company
            ORDER BY	            
            SUBSTRING_INDEX(d.ref_delivery, '_', 1) DESC, 
            CAST(SUBSTRING_INDEX(d.ref_delivery, '_', -1) AS UNSIGNED) DESC;
        """)

        result = db.execute(query, {"document": document, "company": loggedCompany}).mappings().all() # Aquí obtenemos las filas como diccionarios

        if not result:
            raise HTTPException(status_code=404, detail="No hay dispositivos registrados")

        return result  # Ya no necesitas convertir manualmente
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workerExcel/outflows/{document}/{loggedCompany}")       
async def get_worker_excel_outflows(document:str, loggedCompany:str, db:Session=Depends(get_db)):
    try:
        query = text("""
            select o.ref_outflow, o.details, o.price, w.wname, s.date_shift from outflow 
            as o inner join shift as s on o.ref_shift = s.ref_shift 
            inner join premises as p on s.ref_premises = p.ref_premises
            inner join worker as w on s.id = w.id where w.document = :document AND p.company = :company
            ORDER BY	            
            SUBSTRING_INDEX(o.ref_outflow, '_', 1) DESC, 
            CAST(SUBSTRING_INDEX(o.ref_outflow, '_', -1) AS UNSIGNED) DESC;
        """)

        result = db.execute(query, {"document": document, "company": loggedCompany}).mappings().all() # Aquí obtenemos las filas como diccionarios

        if not result:
            raise HTTPException(status_code=404, detail="No hay dispositivos registrados")

        return result  # Ya no necesitas convertir manualmente
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
