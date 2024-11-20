from sqlalchemy.orm import Session
from datetime import datetime
from models.shift import shiftRegistration
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