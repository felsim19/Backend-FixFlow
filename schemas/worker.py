from pydantic import BaseModel as bm
from enum import Enum

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

class workerlogin(bm):
    document:str
    password:str
