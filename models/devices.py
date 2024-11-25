from sqlalchemy import Column, String, ForeignKey
from connection.config import base
from sqlalchemy.orm import relationship

class devicesRegistration(base):
    __tablename__ = "devices"
    id_brands = Column(String(60), ForeignKey('brands.name'))
    name = Column(String(80), primary_key=True)
    
    tbrand = relationship("BrandsRegistration", back_populates="tdevice")