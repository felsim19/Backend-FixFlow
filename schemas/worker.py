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
    shift:Optional[str] = None
    id:str
    is_first_manager:bool = False

class workerlogin(bm):
    document:str
    password:str
