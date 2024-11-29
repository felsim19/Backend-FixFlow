from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.company import status
from schemas.brands import brand
from models.brands import BrandsRegistration
from connection.config import get_db

router = APIRouter()

@router.post("/newBrand", response_model=status)
async def createBrand(brand:brand, db:Session=Depends(get_db)):
    existing_brand = db.query(BrandsRegistration).filter(BrandsRegistration.name == brand.name).first()
    
    if existing_brand:
        raise HTTPException(status_code=403, detail="Esta marca ya esta registrada")
    
    new_brand = BrandsRegistration(
        name=brand.name
    )
    db.add(new_brand)
    db.commit()
    db.refresh(new_brand)
    
    return status(status="Marca registrada exitosamente")

@router.get("/allBrands")
async def get_Brands(db: Session = Depends(get_db)):
    try:
        brands_list = db.query(BrandsRegistration).all()  # Consulta sin filtro
        if not brands_list:
            raise HTTPException(status_code=404, detail="No hay marcas registradas")
        return brands_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))