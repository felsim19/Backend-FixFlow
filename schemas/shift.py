from datetime import date, datetime
from pydantic import BaseModel as bm
from typing import Optional

class shiftclose(bm):
    total_received:float
    total_gain:float
    total_outs:float
    vault:float


class someShift(bm):
    ref_shift:str
    id:str
    document:str
    date_shift:date

class someShiftReceived(bm):
    phone_ref:str
    document:str
    date_shift:date

class addPremiseToShift(bm):
    ref_shift:str
    ref_premises:int

class someShiftSearch(bm):
    ref_shift:str
    ref_premises:int
    start_time:datetime
    id:str
    finish_time:Optional[datetime] 
    document:str
    date_shift:date
