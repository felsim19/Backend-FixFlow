# filepath: c:\Users\felip\OneDrive\Documents\GitHub\Backend-FixFlow\routes\brands.py
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from schemas.company import status
from schemas.brands import brand, idBrand
from models.brands import brandsRegistration
from connection.config import get_db

logging.basicConfig(level=logging.DEBUG)

router = APIRouter()

@router.post("/newBrand/{company}", response_model=status)
async def createBrand(brand: brand, company: str, db: Session = Depends(get_db)):
    existing_brand = db.query(brandsRegistration).filter(brandsRegistration.name == brand.name).filter(
        brandsRegistration.company_user == company
    ).first()

    if existing_brand:
        raise HTTPException(status_code=409, detail="Esta marca ya esta registrada")

    new_brand = brandsRegistration(
        name=brand.name,
        company_user=company
    )
    db.add(new_brand)
    db.commit()
    db.refresh(new_brand)

    return status(status="Marca registrada exitosamente")

@router.get("/allBrands/{company}", response_model=list[brand])
async def get_Brands(company: str, db: Session = Depends(get_db)):
    try:
        query = text("""
            SELECT name from brands where company_user = :company
        """)

        result = db.execute(query, {
            "company": company,  # Permite búsquedas parciales
        }).mappings().all()  # Aquí obtenemos las filas como diccionarios

        if not result:
            raise HTTPException(status_code=404, detail="No hay dispositivos registrados")

        return result  # Ya no necesitas convertir manualmente

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/Brands/{name}/{company}", response_model=list[idBrand])
async def get_idBrands(name: str, company: str, db: Session = Depends(get_db)):
    try:

        query = text("""
            SELECT id from brands where name = :name 
            and company_user = :company
        """)

        result = db.execute(query, {
            "name": name,
            "company": company
        }).mappings().all()

        if not result:
            raise HTTPException(status_code=404, detail="No hay dispositivos registrados")

        return result  # Ya no necesitas convertir manualmente

    except HTTPException as http_exc:
        logging.error(f"HTTPException occurred: {http_exc.detail}")  # Debugging line
        raise http_exc  # Re-raise HTTP exceptions
    except Exception as e:
        logging.error(f"Exception occurred: {e}")  # Debugging line
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

@router.put("/Brands/Edit/{id}", response_model=status)
async def updateBrand(id:int, brand:brand, db:Session=Depends(get_db)):
    try:
        existing_brand = db.query(brandsRegistration).filter(brandsRegistration.id == id).first()   

        if not existing_brand:
            raise HTTPException(status_code=404, detail="Marca no encontrada")

        existing_brand.name = brand.name
        db.commit()
        db.refresh(existing_brand)

        return status(status="Marca actualizada exitosamente")
    except HTTPException:
        raise HTTPException(status_code=500, detail=str(e))
