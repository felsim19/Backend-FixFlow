from datetime import date
from pydantic import BaseModel as bm
from schemas.phone import phone

class bill(bm):
    total_price:float
    client_name:str
    client_phone:str
    wname:str
    ref_shift:str
    phones: list[phone]
    

class someBill(bm):
    bill_number:str
    client_name:str
    entry_date:date

class someBillRepair(bm):
    bill_number:str
    client_name:str
    phone_ref:str

class billRepairPhone(bm):
    due:float
    client_name:str
    payment:float
    bill_number:str

class someDelivery(bm):
    product:str
    sale:float
