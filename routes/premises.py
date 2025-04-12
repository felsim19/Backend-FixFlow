from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from connection.config import get_db
from models.premises import Premises
from schemas.premises import PremisesCreate, PremisesResponse

router = APIRouter(
    prefix="/premises",
    tags=["premises"]
)

@router.post("/", response_model=PremisesResponse)
def create_premises(premises: PremisesCreate, db: Session = Depends(get_db)):
    db_premises = Premises(**premises.dict())
    db.add(db_premises)
    db.commit()
    db.refresh(db_premises)
    return db_premises

@router.get("/", response_model=List[PremisesResponse])
def get_premises(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    premises = db.query(Premises).offset(skip).limit(limit).all()
    return premises

@router.get("/{premises_id}", response_model=PremisesResponse)
def get_premises_by_id(premises_id: int, db: Session = Depends(get_db)):
    premises = db.query(Premises).filter(Premises.id == premises_id).first()
    if premises is None:
        raise HTTPException(status_code=404, detail="Premises not found")
    return premises

@router.put("/{premises_id}", response_model=PremisesResponse)
def update_premises(premises_id: int, premises: PremisesCreate, db: Session = Depends(get_db)):
    db_premises = db.query(Premises).filter(Premises.id == premises_id).first()
    if db_premises is None:
        raise HTTPException(status_code=404, detail="Premises not found")
    
    for key, value in premises.dict().items():
        setattr(db_premises, key, value)
    
    db.commit()
    db.refresh(db_premises)
    return db_premises

@router.delete("/{premises_id}")
def delete_premises(premises_id: int, db: Session = Depends(get_db)):
    db_premises = db.query(Premises).filter(Premises.id == premises_id).first()
    if db_premises is None:
        raise HTTPException(status_code=404, detail="Premises not found")
    
    db.delete(db_premises)
    db.commit()
    return {"message": "Premises deleted successfully"} 