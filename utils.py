from sqlalchemy import desc
from sqlalchemy.orm import Session
from datetime import datetime
from models.shift import shiftRegistration
from models.bill import billRegistrastion
from models.phone import phoneRegistrastion
import re

regex_mail = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

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

def generate_bill_number (db: Session):
    last_bill = db.query(billRegistrastion).order_by(desc(billRegistrastion.bill_number)).first()
    
    if last_bill:
        last_number = last_bill.bill_number[:-2]
        last_letter = last_bill.bill_number[-1]
        
        next_number = int(last_number) + 1
        
        if next_number > 9999:
            next_number = 1 
            last_letter = chr(ord(last_letter) + 1 )

        next_bill_number = f"{next_number:04d}-{last_letter}" 
        
    else:
        next_bill_number = "0001-A"
        
        
    return next_bill_number

def internal_reference (db: Session, bill_number:str):
    # Contar cuántos dispositivos ya están registrados con este número de factura
    devices_count = db.query(phoneRegistrastion).filter(phoneRegistrastion.bill_number == bill_number).count()
    
    # Incrementar el contador con base en el número de dispositivos ya registrados
    contador = devices_count + 1
    
    # Generar la referencia interna con el contador único
    references_int = f"{bill_number}-{contador}"    
    
    return references_int