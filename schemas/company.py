from pydantic import BaseModel as bm

class status(bm):
    status:str

class statusName(bm):
    status:str
    name:str

class company(bm):
    company_user:str
    mail:str
    number:str
    password:str

class companyLogin(bm):
    identifier:str
    password:str

class verificationEmail(bm):
    Email:str

class verificationPin(bm):
    Email:str
    code:int

class NewPassword(bm):
    Email:str
    password:str