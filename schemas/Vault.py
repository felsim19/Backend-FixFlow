from pydantic import BaseModel as bm

class vault(bm):
    ref_shift:str
    quantity:float
