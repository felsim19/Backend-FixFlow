from pydantic import BaseModel as bm

class device(bm):
    id_brands:int
    name:str

class device_name(bm):
    name:str



