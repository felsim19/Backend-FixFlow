from pydantic import BaseModel as bm
from enum import Enum
from typing import Optional
class Wrole(str, Enum):
    admin = "Administrador"
    manager = "Gerente"
    technical = "Tecnico"

class worker(bm):
    wname:str
    password:str
    document:str
    company:str
    wrole: Wrole

class statusworker(bm):
    status:str
    role:str
    wname:str
    shift:str
    id:str
    document:str

class workerlogin(bm):
    document:str
    password:str
    premise_id:Optional[int] = None
