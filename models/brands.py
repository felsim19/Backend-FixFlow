from sqlalchemy import Column, Integer, String,ForeignKey
from connection.config import base
from sqlalchemy.orm import relationship


class brandsRegistration(base):
    __tablename__ = "brands"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(60), nullable=False)
    company_user = Column(String(50), ForeignKey("company.company_user"), nullable=False)
    
    tphone = relationship("phoneRegistrastion", back_populates="tbrand")
    tcompany = relationship("companyRegistration", back_populates="tbrand")
    tdevice = relationship("devicesRegistration", back_populates="tbrand")  