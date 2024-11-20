from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.company import status
from schemas.worker import worker, statusworker, workerlogin as wl
from models.company import companyRegistration
from models.worker import workerRegistrastion
from models.shift import shiftRegistration
from connection.config import get_db
from utils import generate_shift_reference
import bcrypt

router = APIRouter()


@router.post("/insertWorker", response_model=status)
async def insertWorker(worker:worker, db:Session=Depends(get_db)):
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
        wname = worker.wname,
        password = encryption.decode('utf-8'),
        document = worker.document,
        company = worker.company,
        wrole = assigned_role
    )
    db.add(new_worker)
    db.commit()
    db.refresh(new_worker)
    return status(status="Trabajador registrado exitosamente", msg="registro exitoso")

@router.get("/company/{company_id}/workers/count")
async def get_worker_count(company_id:str, db:Session=Depends(get_db)): 
    count = db.query(workerRegistrastion).filter(workerRegistrastion.company == company_id).count()
    return {"count" : count }

@router.get("/collaborators/{company_id}/workers")
async def get_collaborators( company_id:str, db:Session = Depends(get_db)):
    clb_list = db.query(workerRegistrastion).filter(workerRegistrastion.company == company_id).all()
    return clb_list

@router.post("/loginWorker/{company_id}", response_model=statusworker)
async def loginworker(company_id: str, worker_user: wl, db: Session = Depends(get_db)):
    # Buscar al trabajador en la base de datos
    db_worker = db.query(workerRegistrastion).filter(
        workerRegistrastion.document == worker_user.document,
        workerRegistrastion.company == company_id
    ).first()

    # Validar que el trabajador exista
    if db_worker is None:
        raise HTTPException(status_code=400, detail="Nombre de usuario no existe")

    # Validar la contraseña
    if not bcrypt.checkpw(worker_user.password.encode('utf-8'), db_worker.password.encode('utf-8')):
        raise HTTPException(status_code=401, detail="Contraseña Incorrecta")

    # Registrar la hora de inicio del turno
    now = datetime.now()
    new_shift = shiftRegistration(
        document=db_worker.document,
        start_time=now,
        ref_shift= generate_shift_reference(db)
    )
    db.add(new_shift)
    db.commit()

    # Retornar la respuesta de inicio de sesión con rol y confirmación
    return {
        "status": "Inicio de sesión exitoso",
        "role": db_worker.wrole,
        "wname": db_worker.wname
    }