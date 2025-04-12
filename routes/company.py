from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi.responses import RedirectResponse
from fastapi import APIRouter, Depends, HTTPException
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from sqlalchemy.orm import Session
from schemas.company import company, status, statusName, companyLogin, verificationEmail, verificationPin, NewPassword
from schemas.Vault import vault
from models.company import companyRegistration
from models.VaultOut import outVaultRegistration
from models.recoveryPassword import PasswordRecovery
from connection.config import get_db
from utils import is_valid_mail, generate_pin, create_verification_token
from dotenv import load_dotenv
import bcrypt
import os

load_dotenv()


conf = ConnectionConfig(
    MAIL_USERNAME= os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT =os.getenv("MAIL_PORT"),
    MAIL_SERVER = os.getenv("MAIL_SERVER"),
    MAIL_FROM_NAME="Fixflow",
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)

router = APIRouter()

@router.post("/insertCompany", response_model=status)
async def insertCompany(company: company, db: Session = Depends(get_db)):
    try:
        if not is_valid_mail(company.mail):
            raise HTTPException(status_code=401, detail="Correo no válido")
            
        name_company = db.query(companyRegistration).filter(
            companyRegistration.company_user == company.company_user).first()
        if name_company:
            raise HTTPException(status_code=401, detail="Compañía ya existente")

        encriptacion = bcrypt.hashpw(company.password.encode("utf-8"), bcrypt.gensalt())
        data = companyRegistration(
            company_user=company.company_user,
            mail=company.mail,
            number=company.number,
            password=encriptacion.decode('utf-8')
        )
        db.add(data)
        db.commit()
        db.refresh(data)

        # Crear token de verificación
        verification_token = create_verification_token(company.mail)
        
        # URL de verificación (usa tu dominio real en producción)
        verification_url = f"http://localhost:8000/api/verify-email?token={verification_token}&redirect_to=http://localhost:5173/loginCompany"
        
        # Enviar email
        msg = MessageSchema(
            subject="Verifica tu email - Fixflow",
            recipients=[company.mail],
            body=f"""
            <h1>Bienvenido a Fixflow</h1>
            <p>Por favor verifica tu email haciendo clic en el siguiente enlace:</p>
            <a href="{verification_url}">Verificar email</a>
            <p>Este enlace expirará en 24 horas.</p>
            """,
            subtype="html"
        )
        
        fm = FastMail(conf)
        await fm.send_message(msg)
        
        return status(status="La compañía ha sido registrada. Por favor verifica tu email.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/verify-email")
async def verify_email(token: str, redirect_to: str, db: Session = Depends(get_db)):
    try:
        # Verificar el token
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
        email = payload.get("sub")
        if not email:
            return RedirectResponse(url=f"{redirect_to}?error=invalid_token")
        
        # Buscar la compañía
        company = db.query(companyRegistration).filter(
            companyRegistration.mail == email,
            companyRegistration.verifiedMail == 0  # Cambiar a is_verified si usas ese nombre
        ).first()
        
        if not company:
            return RedirectResponse(url=f"{redirect_to}?error=already_verified_or_not_found")
        
        # Actualizar el estado de verificación
        company.verifiedMail = 1  # O company.is_verified = True
        db.commit()
        
        # Redirigir al frontend con éxito
        return RedirectResponse(url=f"{redirect_to}?verified=success")
    
    except JWTError:
        return RedirectResponse(url=f"{redirect_to}?error=invalid_token")
    except Exception as e:
        print(f"Error en verificación: {str(e)}")
        return RedirectResponse(url=f"{redirect_to}?error=server_error")

@router.post("/loginCompany", response_model=statusName)
async def loginCompany(company_user:companyLogin, db:Session=Depends(get_db)):
    try:
        db_company = db.query(companyRegistration).filter(
            (companyRegistration.company_user == company_user.identifier ) |
            (companyRegistration.mail == company_user.identifier)).first()
        if db_company is None:
            raise HTTPException(status_code=400, detail="Compañia no existe")
        if db_company.verifiedMail == 0:
            raise HTTPException(status_code=403, detail="Por favor verifica tu email primero")
        if not bcrypt.checkpw(company_user.password.encode('utf-8'), db_company.password.encode('utf-8')):
            raise HTTPException(status_code=401, detail="Contraseña Incorrecta")
        return {
            "status" : "Inicio de sesion exitoso",
            "name" : db_company.company_user
        }
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
    

@router.get("/company/{loggedCompany}/baseColor")
async def get_company_color(loggedCompany:str, db:Session=Depends(get_db)):
    try:
        company = db.query(companyRegistration).filter(companyRegistration.company_user == loggedCompany).first()
        if not company:
            raise HTTPException(status_code=404, detail="Compañia no encontrada")
        return {"baseColor" : company.base_color}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/company/{loggedCompany}/number")
async def get_company_number(loggedCompany:str, db:Session=Depends(get_db)):
    try:
        company = db.query(companyRegistration).filter(companyRegistration.company_user == loggedCompany).first()
        if not company:
            raise HTTPException(status_code=404, detail="Compañia no encontrada")
        return {"number" : company.number}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/company/{loggedCompany}/baseColor/{color}", response_model=status)
async def get_company_vault(loggedCompany:str,color:str, db:Session=Depends(get_db)): 
    try:
        company = db.query(companyRegistration).filter(companyRegistration.company_user == loggedCompany).first()
        if not company:
            raise HTTPException(status_code=404, detail="Compañia no encontrada")
        company.base_color = color
        db.commit()
        db.refresh(company)
        return status(status="Color base actualizado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/OutFlowVault/{loggedcompany}", response_model=status)
async def OutFlowVault(loggedcompany:str, changes:vault, db:Session=Depends(get_db)):
    try:
        company = db.query(companyRegistration).filter(companyRegistration.company_user == loggedcompany).first()
        if not company:
            raise HTTPException(status_code=404, detail="Compañia no encontrada")
        if changes.quantity > company.vault:
            raise HTTPException(status_code=401, detail="No hay suficiente dinero en caja")
        company.vault -= changes.quantity
        db.commit()
        db.refresh(company)

        data = outVaultRegistration(
            ref_shift = changes.ref_shift,
            quantity = changes.quantity
        )
        db.add(data)
        db.commit() 
        db.refresh(data)
        return status(status="Cambio de caja registrado correctamente")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/passwordRecovery", response_model=status)
async def forggetPassword(emailUser: verificationEmail, db: Session = Depends(get_db)):
    try:
        db_company = db.query(companyRegistration).filter(companyRegistration.mail == emailUser.Email).first()
        if db_company is None:
            raise HTTPException(status_code=400, detail="Compañia no existe")
        
        pin = generate_pin(6)
        expiration_time = datetime.now() + timedelta(minutes=15)  # Usar timedelta directamente

        # Verificar si ya existe un registro de recuperación para esta compañía
        existing_recovery = db.query(PasswordRecovery).filter(
            PasswordRecovery.company == db_company.company_user
        ).first()
        
        if existing_recovery:
            # Actualizar el registro existente
            existing_recovery.pin = pin
            existing_recovery.expires_at = expiration_time
        else:
            # Crear nuevo registro
            data = PasswordRecovery(
                company=db_company.company_user,
                pin=pin,
                expires_at=expiration_time
            )
            db.add(data)
        
        db.commit()

        msg = MessageSchema(
            subject="Recuperación de contraseña",
            recipients=[emailUser.Email],
            body=f"Su PIN es: {pin} \nEste PIN es válido por 15 minutos",
            subtype="html"
        )
        
        fm = FastMail(conf)
        await fm.send_message(msg)
        return status(status="Se ha enviado un correo con el pin de recuperación")
    except Exception as e:
        db.rollback()  # Asegurarse de hacer rollback en caso de error
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/verify-pin", response_model=status)
async def verify_pin(verification:verificationPin, db: Session = Depends(get_db)):
    try:
        # Recuperar el registro de PIN según la empresa (según el email)
        recovery_entry = db.query(PasswordRecovery).join(companyRegistration)\
                        .filter(companyRegistration.mail == verification.Email)\
                        .order_by(PasswordRecovery.expires_at.desc()).first()
        
        if not recovery_entry:
            raise HTTPException(status_code=400, detail="No se encontró solicitud de recuperación")
        
        # Verificar que el PIN no haya expirado
        if datetime.now() > recovery_entry.expires_at:
            raise HTTPException(status_code=400, detail="El PIN ha expirado")
        
        # Verificar que el PIN ingresado sea el correcto
        if recovery_entry.pin != verification.code:
            raise HTTPException(status_code=400, detail="El PIN ingresado es incorrecto")
        return status(status="el pin de recuperacion es correcto")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/confirmPassword", response_model=status)
async def insertCompany(changes:NewPassword,db:Session=Depends(get_db)):
    try:
        company = db.query(companyRegistration).filter(companyRegistration.mail==changes.Email).first()
        encriptacion = bcrypt.hashpw(changes.password.encode("utf-8"), bcrypt.gensalt())
        company.password = encriptacion.decode('utf-8')
        db.commit()
        db.refresh(company)
        return status(status="La compañia a cambiado de contraseña correctamente")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/resend-confirmation-code", response_model=status)
async def resend_confirmation_code(emailUser: verificationEmail, db: Session = Depends(get_db)):
    try:
        db_company = db.query(companyRegistration).filter(companyRegistration.mail == emailUser.Email).first()
        if db_company is None:
            raise HTTPException(status_code=400, detail="Compañia no existe")
        
        # Verificar si ya existe un PIN activo
        existing_recovery = db.query(PasswordRecovery).filter(
            PasswordRecovery.company == db_company.company_user
        ).first()
        
        if existing_recovery and datetime.now() < existing_recovery.expires_at:
            # Reenviar el mismo PIN si aún es válido
            pin = existing_recovery.pin
            expiration_time = existing_recovery.expires_at
        else:
            # Generar nuevo PIN si no existe o ha expirado
            pin = generate_pin(6)
            expiration_time = datetime.now() + timedelta(minutes=15)
            
            if existing_recovery:
                # Actualizar registro existente
                existing_recovery.pin = pin
                existing_recovery.expires_at = expiration_time
            else:
                # Crear nuevo registro
                data = PasswordRecovery(
                    company=db_company.company_user,
                    pin=pin,
                    expires_at=expiration_time
                )
                db.add(data)
        
        db.commit()

        # Enviar el correo
        msg = MessageSchema(
            subject="Confrimacion del Correo - Nuevo código",
            recipients=[emailUser.Email],
            body=f"Su nuevo PIN es: {pin} \nEste PIN es válido por 15 minutos",
            subtype="html"
        )
        
        fm = FastMail(conf)
        await fm.send_message(msg)
        
        return status(status="Se ha reenviado el código de confirmación a su correo")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


