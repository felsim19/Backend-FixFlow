from datetime import date
from pydantic import BaseModel as bm

class shiftclose(bm):
    total_received:float
    total_gain:float
    total_outs:float
    vault:float


class someShift(bm):
    ref_shift:str
    document:str
    date_shift:date

class someShiftReceived(bm):
    phone_ref:str
    document:str
    date_shift:date