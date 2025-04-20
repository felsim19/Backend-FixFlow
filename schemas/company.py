from pydantic import BaseModel as bm
from enum import Enum

class status(bm):
    status:str

class plan(str, Enum):
    basic = "Basico"
    pro = "Pro"
    premium = "Premium"

class statusName(bm):
    status:str
    name:str


class company(bm):
    company_user:str
    mail:str
    number:str
    password:str
    subscription_plan:plan
    subscription_price:float


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