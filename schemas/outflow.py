from pydantic import BaseModel as bm

class outflow(bm):
    ref_shift: str
    details: str
    price: float