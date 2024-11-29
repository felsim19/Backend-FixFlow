from sqlalchemy import String, Column, Float, ForeignKey, Integer
from connection.config import base
from sqlalchemy.orm import relationship

class deliveryRegistration(base):
    __tablename__ = "delivery"
    ref_delivery = Column(Integer,primary_key=True, autoincrement=True)
    ref_shift = Column(String(60), ForeignKey("shift.ref_shift"), nullable=False)
    product = Column(String(60), nullable=False)
    sale = Column(Float(), nullable=False)
    original_price = Column(Float(), nullable=False)
    revenue_price = Column(Float(), nullable=False)

    tshift = relationship("shiftRegistration", back_populates="tdelivery")  