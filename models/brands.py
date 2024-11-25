from sqlalchemy import Column, Integer, String
from connection.config import base
from sqlalchemy.orm import relationship


class BrandsRegistration(base):
    __tablename__ = "brands"
    id = Column(Integer,unique=True , autoincrement=True) 
    name = Column(String(60),primary_key=True, index=True)        
    
    tphone = relationship("phoneRegistrastion", back_populates="tbrand")
    tdevice = relationship("devicesRegistration", back_populates="tbrand")