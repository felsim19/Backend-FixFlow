from pydantic import BaseModel as bm

class brand(bm):
    name:str   

class idBrand(bm):
    id:int  