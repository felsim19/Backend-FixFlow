from pydantic import BaseModel as bm
from datetime import date

class phone(bm):
    brand_name:str
    brand_id:int
    due:float
    payment:float
    device:str
    details:str
    individual_price:int


class somePhone(bm):
    phone_ref:str
    brand_name:str
    device:str
    details:str
    entry_date:date

class pricePhone(bm):
    individual_price:int