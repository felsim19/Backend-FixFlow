from pydantic import BaseModel as bm

class delivery(bm):
    ref_shift: str
    product: str
    sale: float
    original_price: float
    revenue_price: float

class deliveryExcel(bm):
    ref_delivery: int
    product: str
    sale: float
    original_price: float
    revenue_price: float
