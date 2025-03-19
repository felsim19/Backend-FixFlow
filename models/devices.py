from sqlalchemy import Column, String, ForeignKey, Integer
from connection.config import base
from sqlalchemy.orm import relationship

class devicesRegistration(base):
    __tablename__ = "devices"
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_brands = Column(Integer, ForeignKey('brands.id'))
    name = Column(String(80), nullable=False)
    
    tbrand = relationship("brandsRegistration", back_populates="tdevice")