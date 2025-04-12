from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.company import status
from schemas.worker import worker, statusworker, workerlogin as wl
from models.company import companyRegistration
from models.worker import workerRegistrastion
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
        workers_count = db.query(workerRegistrastion).filter(workerRegistrastion.company == worker.company).count()
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
        
        new_worker = workerRegistrastion(
            id = get_words_worker(nameCompany, worker.document),
            wname = worker.wname,
            password = encryption.decode('utf-8'),
            document = worker.document,
            company = worker.company,
            wrole = assigned_role,
            active = True
        )
        
        id = db.query(workerRegistrastion).filter(workerRegistrastion.id == new_worker.id).first()
        if id:  
            raise HTTPException(status_code=401, detail="El documento ya existe.")
        
        db.add(new_worker)
        db.commit()
        db.refresh(new_worker)
        return status(status="Trabajador registrado exitosamente", msg="registro exitoso")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/company/{company_id}/count")
async def get_worker_count(company_id:str, db:Session=Depends(get_db)): 
    try:
        count = db.query(workerRegistrastion).filter(workerRegistrastion.company == company_id).count()
        return {"count" : count }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/collaborators/{company_id}/workers")
async def get_collaborators( company_id:str, db:Session = Depends(get_db)):
    try:
        clb_list = db.query(workerRegistrastion).filter(workerRegistrastion.company == company_id).all()
        return clb_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/loginWorker/{company_id}", response_model=statusworker)
async def loginworker(company_id: str, worker_user: wl, db: Session = Depends(get_db)):
    try:
        # Buscar al trabajador en la base de datos
        db_worker = db.query(workerRegistrastion).filter(
            workerRegistrastion.id == get_words_worker(company_id, worker_user.document),
            workerRegistrastion.company == company_id
        ).first()

        # Validar que el trabajador exista
        if db_worker is None:
            raise HTTPException(status_code=400, detail="Nombre de usuario no existe")
        
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
            ref_shift= generate_shift_reference(db)
        )
        db.add(new_shift)
        db.commit()

        # Retornar la respuesta de inicio de sesión con rol y confirmación
        return {
            "status": "Inicio de sesión exitoso",
            "role": db_worker.wrole,
            "wname": db_worker.wname,
            "shift": new_shift.ref_shift,
            "id": db_worker.id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/inactiveCollaborators/{company_id}/{document}", response_model=status)
async def delete_collaborators(company_id:str,document:str, db:Session = Depends(get_db)):
    try:
        worker = db.query(workerRegistrastion).filter(
            workerRegistrastion.company == company_id,
            workerRegistrastion.document == document
            ).first()
        
        if worker is None:
                raise HTTPException(status_code=404,detail="Trabajador no encontrado")
            
        worker.active = False
        db.commit()
        db.refresh(worker)
        return status(status="trabajador inactivado exitosamente")  
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/reactiveCollaborators/{company_id}/{document}", response_model=status)
async def delete_collaborators(company_id:str,document:str, db:Session = Depends(get_db)):
    try:
        worker = db.query(workerRegistrastion).filter(
            workerRegistrastion.company == company_id,
            workerRegistrastion.document == document
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
        worker = db.query(workerRegistrastion).filter(workerRegistrastion.document == workerDocument, 
                                                     workerRegistrastion.company == company).first()
        
        if worker is None:
            raise HTTPException(status_code=404, detail="Trabajador no encontrado")
            
        return {"wname" : worker.wname }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))