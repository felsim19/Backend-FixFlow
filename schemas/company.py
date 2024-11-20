from pydantic import BaseModel as bm

class status(bm):
    status:str

class statusName(bm):
    status:str
    name:str

class company(bm):
    company_user:str
    mail:str
    password:str

class companyLogin(bm):
    identifier:str
    password:str
