from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from schemas.company import company, status, statusName, companyLogin
from models.company import companyRegistration
from connection.config import get_db
from utils import is_valid_mail
import bcrypt

router = APIRouter()

@router.post("/insertCompany", response_model=status)
async def insertCompany(company:company,db:Session=Depends(get_db)):
    try:
        if not is_valid_mail(company.mail):
            raise HTTPException(status_code=401,detail="Correo no valido")
        name_company = db.query(companyRegistration).filter(companyRegistration.company_user==company.company_user).first()
        if name_company:
            raise HTTPException(status_code=401,detail="compañia ya existente")
        encriptacion = bcrypt.hashpw(company.password.encode("utf-8"), bcrypt.gensalt())
        data = companyRegistration(
            company_user=company.company_user,
            mail=company.mail,
            password=encriptacion.decode('utf-8')
        )
        db.add(data)
        db.commit()
        db.refresh(data)
        return status(status="La compañia a sido registrada correctamente")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/loginCompany", response_model=statusName)
async def loginCompany(company_user:companyLogin, db:Session=Depends(get_db)):
    try:
        db_company = db.query(companyRegistration).filter(
            (companyRegistration.company_user == company_user.identifier ) |
            (companyRegistration.mail == company_user.identifier)).first()
        if db_company is None:
            raise HTTPException(status_code=400, detail="Compañia no existe")
        if not bcrypt.checkpw(company_user.password.encode('utf-8'), db_company.password.encode('utf-8')):
            raise HTTPException(status_code=401, detail="Contraseña Incorrecta")
        return {
            "status" : "Inicio de sesion exitoso",
            "name" : db_company.company_user
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/putCompanyImage/{loggedCompany}", response_model=status)
async def putCompanyImage(loggedCompany:str, file: UploadFile = File(...) ,db:Session=Depends(get_db)):
    #Bucar la compañia
    try:
        company = db.query(companyRegistration).filter(companyRegistration.company_user == loggedCompany).first()
        image_content = await file.read()
        url_image = f"static/{file.filename}"  
        
        file_location = f"companyImg/{file.filename}"
        with open(file_location, "wb") as buffer:
            buffer.write(image_content)
        company.url_image = url_image
        db.commit()  # Guardar los cambios
        db.refresh(company)  # Opcional: refrescar el objeto company con los nuevos datos

        return status(status="Image updated successfully")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/allcompany/{loggedCompany}", response_model=status)
async def getImageCompany(loggedCompany: str, db: Session = Depends(get_db)):
    try:
        # Consulta la base de datos
        company = db.query(companyRegistration).filter(companyRegistration.company_user == loggedCompany).first()

        # Verifica si existe la compañía
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")

        return status(status=company.url_image)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/company/{company_id}/vault/baseColor")
async def get_company_vault(company_id:str, db:Session=Depends(get_db)): 
    try:
        company = db.query(companyRegistration).filter(companyRegistration.company_user == company_id).first()
        if not company:
            raise HTTPException(status_code=404, detail="Compañia no encontrada")
        return {"vault" : company.vault, 
                "baseColor" : company.base_color}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


