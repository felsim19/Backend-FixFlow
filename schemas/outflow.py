from pydantic import BaseModel as bm
from datetime import date
class outflow(bm):
    ref_shift: str
    details: str
    price: float

class someOutflow(bm):
    details: str
    price: float

class outflowExcel(bm):
    ref_outflow: int
    details: str
    price: float
    wname: str
    date_shift: date
