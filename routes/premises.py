from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from connection.config import get_db
from models.premises import premisesRegistration
from models.company import companyRegistration
from schemas.company import status
from schemas.premises import premises


router = APIRouter()

@router.get("/premises/{company_id}/count")
async def get_worker_count(company_id:str, db:Session=Depends(get_db)): 
    try:
        count = db.query(premisesRegistration).filter(premisesRegistration.company == company_id).count()
        return {"count" : count }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/newPremises/{loggedCompany}", response_model=status)
async def newPremises(loggedCompany:str, premises:premises, db:Session=Depends(get_db)):
    try:
        company = db.query(companyRegistration).filter(companyRegistration.company_user == loggedCompany).first()
        if not company:
            raise HTTPException(status_code=404, detail="Compañia no encontrada")
        new_premises = premisesRegistration(
            name=premises.name,
            address=premises.address,
            password=premises.password,
            company=loggedCompany
        )
        new_premises.active = True
        db.add(new_premises)
        db.commit()
        db.refresh(new_premises)
        return status(status="Sucursal creada correctamente")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))