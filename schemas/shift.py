from datetime import datetime
from pydantic import BaseModel as bm

class shiftclose(bm):
    total_received:float
    total_gain:float


class someShift(bm):
    ref_shift:str
    document:str
    start_time:datetime