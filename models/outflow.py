from sqlalchemy import String, Column, Float, ForeignKey, Integer
from connection.config import base
from sqlalchemy.orm import relationship

class outflowRegistration(base):
    __tablename__ = "outflow"
    ref_outflow = Column(Integer,primary_key=True, autoincrement=True)
    ref_shift = Column(String(60), ForeignKey("shift.ref_shift"), nullable=False)
    price = Column(Float(), nullable=False)

    tshift = relationship("shiftRegistration", back_populates="toutflow")