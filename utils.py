from sqlalchemy import desc
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from fastapi import Request
from datetime import datetime, timedelta
from models.shift import shiftRegistration
from models.bill import billRegistrastion
from models.phone import phoneRegistrastion
import hashlib
import re
import random
import os
import string


regex_mail = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

def generate_payment_id(company: str, plan: str) -> str:
    """
    Genera un ID de pago con formato fixflow-{plan}-{timestamp}
    
    Args:
        company (str): Nombre de la compañía (no se usa en el formato actual, pero se recibe por compatibilidad)
        plan (str): Nombre del plan (ej: 'basic', 'premium', etc)
    
    Returns:
        str: ID de pago generado con formato fixflow-{plan}-{timestamp}
    """
    # Obtener el timestamp actual en milisegundos
    timestamp = int(datetime.now().timestamp() * 1000)
    
    # Generar el payment_id en el formato deseado
    payment_id = f"{company}-{plan}-{timestamp}"
    
    return payment_id

def calculate_payment_date(date_start: date) -> datetime:
    """
    Calcula la fecha de pago basada en la fecha de inicio.
    La fecha de pago será 1 mes y 5 días después de la fecha de inicio.
    
    Args:
        date_start: Fecha de inicio de la suscripción
        
    Returns:
        datetime: Fecha de pago calculada
    """
    # Convertir date a datetime si es necesario
    if isinstance(date_start, date):
        date_start = datetime.combine(date_start, datetime.min.time())
    
    # Añadir 1 mes usando relativedelta para manejar correctamente los cambios de mes
    one_month_later = date_start + relativedelta(months=1)
    
    # Añadir 5 días adicionales
    payment_date = one_month_later + timedelta(days=5)
    
    return payment_date

def is_valid_mail(mail:str) -> bool:
    return re.match(regex_mail,mail) is not None

def generate_shift_reference(db: Session):
    today_date = datetime.now().strftime("%Y%m%d")
    
    # Contar turnos existentes del día
    daily_shifts = db.query(shiftRegistration).filter(
        shiftRegistration.start_time.like(f"{datetime.now().date()}%")
    ).count()
    
    # Generar la referencia
    shift_reference = f"{today_date}_{daily_shifts + 1}"
    return shift_reference

def generate_bill_number(db: Session, company_user: str):
    last_bill = (
        db.query(billRegistrastion)
        .filter(billRegistrastion.bill_number.like(f"{company_user}-%"))
        .order_by(desc(billRegistrastion.bill_number))
        .first()
    )

    if last_bill:
        last_number = last_bill.bill_number.split('-')[1]
        last_letter = last_bill.bill_number.split('-')[2]
        
        next_number = int(last_number) + 1
        if next_number > 9999:
            next_number = 1
            last_letter = chr(ord(last_letter) + 1)
        
        next_bill_number = f"{company_user}-{next_number:04d}-{last_letter}"
    else:
        next_bill_number = f"{company_user}-0001-A"
    
    return next_bill_number


def internal_reference (db: Session, bill_number:str):
    # Contar cuántos dispositivos ya están registrados con este número de factura
    devices_count = db.query(phoneRegistrastion).filter(phoneRegistrastion.bill_number == bill_number).count()
    
    # Incrementar el contador con base en el número de dispositivos ya registrados
    contador = devices_count + 1
    
    # Generar la referencia interna con el contador único
    references_int = f"{bill_number}-{contador}"    
    
    return references_int

def get_words_worker(company, document):
    return company + "_" + document

def generate_pin(digit:6):
    return random.randint(10**(digit-1), (10**digit)-1)


def create_verification_token(email: str):
    expire_minutes = int(os.getenv("VERIFY_TOKEN_EXPIRE", "1440"))  # Conversión a int
    expire = datetime.utcnow() + timedelta(minutes=expire_minutes)
    to_encode = {"sub": email, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, os.getenv("SECRET_KEY"), algorithm=os.getenv("ALGORITHM"))
    return encoded_jwt

def generateDataIntegrity(Identifier, Amount, Currency):
    """
    Genera una firma de integridad para la API de Bold
    
    Args:
        Identifier: Identificador único del pago
        Amount: Monto del pago
        Currency: Moneda del pago
        
    Returns:
        str: Firma de integridad en formato hexadecimal
    """
    # Obtener la clave secreta desde las variables de entorno
    SecretKey = os.getenv("BOLD_SECRET_KEY", "")
    
    # Verificar que la clave secreta esté disponible
    if not SecretKey:
        raise ValueError("BOLD_SECRET_KEY no está configurada en las variables de entorno")
    
    # Concatenar los valores para generar la firma
    cadena_concatenada = f"{Identifier}{Amount}{Currency}{SecretKey}"
    
    # Crear un objeto hash SHA-256
    m = hashlib.sha256()
    # Actualizar el objeto hash con la cadena codificada en UTF-8
    m.update(cadena_concatenada.encode())
    # Obtener el hash en formato hexadecimal
    hash_hex = m.hexdigest()
    # Imprimir el hash
    return hash_hex
