from sqlalchemy import Column,String,Float,Date, func, ForeignKey
from connection.config import base
from sqlalchemy.orm import relationship
from datetime import date

class billRegistrastion(base):  
    __tablename__ = "bill"
    bill_number = Column(String(50), primary_key=True, nullable=False)
    total_price = Column(Float(), nullable=False)
    entry_date = Column(Date(), default=date.today, nullable=False)
    client_name = Column(String(30), nullable=False)
    client_phone = Column(String(20), nullable=False)
    ref_shift = Column(String(60), ForeignKey('shift.ref_shift') ,nullable=False)
    wname = Column(String(50), nullable=False)
    
    tphone = relationship("phoneRegistrastion", back_populates="tbill")
    tshift = relationship("shiftRegistration", back_populates="tbill")
    treparation = relationship("reparationRegistration", back_populates="tbill")

