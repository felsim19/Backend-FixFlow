from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models.subscription import SubscriptionRegistration
from connection.config import get_db


router = APIRouter()

@router.get("/company/subscription/{loggedCompany}")
async def get_company_number(loggedCompany: str, db: Session = Depends(get_db)):
    try:
        companyPlanSubscription = (
            db.query(SubscriptionRegistration)
            .filter(SubscriptionRegistration.company == loggedCompany)
            .first()
        )
        if not companyPlanSubscription:
            raise HTTPException(status_code=404, detail="suscripcion no encontrada")
        return {"planCompany": companyPlanSubscription.plan}
    except Exception as e:  
        raise HTTPException(status_code=500, detail=str(e))
    
@router.put("/company/plan/{loggedCompany}/{newPlan}")
async def update_company_plan(loggedCompany: str, newPlan: str, db: Session = Depends(get_db)):
    try:
        companyPlanSubscription = (
            db.query(SubscriptionRegistration)
            .filter(SubscriptionRegistration.company == loggedCompany)
            .first()
        )
        if not companyPlanSubscription:
            raise HTTPException(status_code=404, detail="suscripcion no encontrada")
        companyPlanSubscription.plan = newPlan
        db.commit()
        return {"message": "plan actualizado correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

