from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from connection.config import get_db
from models.premises import premisesRegistration

router = APIRouter()

@router.get("/premises/{company_id}/count")
async def get_worker_count(company_id:str, db:Session=Depends(get_db)): 
    try:
        count = db.query(premisesRegistration).filter(premisesRegistration.company == company_id).count()
        return {"count" : count }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))