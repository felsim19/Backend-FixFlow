from pydantic import BaseModel as bm
from enum import Enum

class typePremises(str, Enum):
    repairService = "Servicio de reparacion de celulares"
    sellService = "Venta de accesorios"
    other = "Otro"

class premises(bm):
    name:str
    address:str
    password:str
    company:str
    
