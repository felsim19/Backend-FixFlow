from sqlalchemy import Column,String,ForeignKey,Integer,Boolean,Date,Float
from connection.config import base
from sqlalchemy.orm import relationship

class phoneRegistrastion(base):
    __tablename__ = "phone"
    phone_ref = Column(String(60), primary_key=True, nullable=False)
    bill_number = Column(String(60),ForeignKey('bill.bill_number') ,nullable=False)
    brand_name = Column(String(50), nullable=False)
    brand_id = Column(Integer, ForeignKey('brands.id'),nullable=False)
    device = Column(String(50), nullable=False)
    details = Column(String(250), nullable=False)
    individual_price = Column(Integer, nullable=False)
    due = Column(Float(), nullable=False)
    payment = Column(Float())
    repaired = Column(Boolean(),default=False)
    delivered = Column(Boolean(),default=False)
    date_delivered = Column(Date())
    
    tbrand = relationship("brandsRegistration", back_populates="tphone")
    tbill = relationship("billRegistrastion", back_populates="tphone")
    treparation = relationship("reparationRegistration", back_populates="tphone")