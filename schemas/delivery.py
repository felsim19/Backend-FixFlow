from pydantic import BaseModel as bm
from datetime import date
class delivery(bm):
    ref_shift: str
    product: str
    sale: float
    original_price: float
    revenue_price: float

class deliveryExcel(bm):
    ref_delivery: int
    date_shift: date
    product: str
    sale: float
    original_price: float
    revenue_price: float
    wname: str
    
