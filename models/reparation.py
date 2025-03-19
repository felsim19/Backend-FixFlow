from sqlalchemy import Column, Integer, String, ForeignKey
from connection.config import base
from sqlalchemy.orm import relationship

class reparationRegistration(base):
    __tablename__ = "reparation"
    ref = Column(Integer, primary_key=True, autoincrement=True) 
    ref_shift = Column(String(60), ForeignKey("shift.ref_shift"), nullable=False) 
    phone_ref = Column(String(60), ForeignKey("phone.phone_ref"), nullable=False)
    bill_number = Column(String(60), ForeignKey("bill.bill_number"), nullable=False)  

    tphone = relationship("phoneRegistrastion", back_populates="treparation")
    tshift = relationship("shiftRegistration", back_populates="treparation")
    tbill = relationship("billRegistrastion", back_populates="treparation")  
