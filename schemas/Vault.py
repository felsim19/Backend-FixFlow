from pydantic import BaseModel as bm

class vault(bm):
    ref_premises:int
    quantity:float
    wname:str