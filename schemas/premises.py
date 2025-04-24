from pydantic import BaseModel as bm
from enum import Enum
from typing import Optional
from datetime import datetime

class typePremises(str, Enum):
    repairService = "Servicio de reparacion de celulares"
    sellService = "Venta de accesorios"
    other = "Otro"

class premises(bm):
    name:str
    address:str
    password:str
    company:str

class premisesCompany(bm):
    name:str
    ref_premises:int
    company:str 
    
class somePremises(bm):
    ref_premises:int
    name:str
    address:str
    active:bool
    
class loginPremises(bm):
    premise_id:int
    password:str
    startShift:Optional[str] = None

class editPremises(bm):
    ref_premises:int
    name:str
    address:str

class somePremisesOutVault(bm):
    wname:str
    date:datetime
    quantity:float

    

