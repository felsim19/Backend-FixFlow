from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models.company import companyRegistration
from models.subscription import SubscriptionRegistration
from connection.config import get_db
from utils import generateDataIntegrity, generate_payment_id
from schemas.subcription import PaymentSubscription


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
    
@router.put("/company/plan/{loggedCompany}/{newPlan}/{quantityPremises}")
async def update_company_plan(loggedCompany: str, newPlan: str, quantityPremises: int, db: Session = Depends(get_db)):
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
        company = db.query(companyRegistration).filter(companyRegistration.company_user == loggedCompany).first()
        company.quantity_premises = quantityPremises
        db.commit()
        db.refresh(company)
        return {"message": "plan actualizado correctamente"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))




@router.get("/subscription/hash")
async def getHash(identifier: str, amount: str, currency: str):
    try:
        data_integrity = generateDataIntegrity(identifier, amount, currency)
        return {"data_integrity": data_integrity}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/suscription/orderId/{company}/{plan}")
async def getOrderId(company: str, plan: str):
    try:
        orderId = generate_payment_id(company, plan)
        return {"orderId": orderId}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/suscription/status/{company}")
async def getStatusCompany(company: str, db: Session = Depends(get_db)):
    try:
        payment = db.query(SubscriptionRegistration).filter(SubscriptionRegistration.company == company).first()
        return {"status": payment.active}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
