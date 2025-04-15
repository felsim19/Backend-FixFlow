from sqlalchemy import String, Column, Float, ForeignKey, Integer, DateTime
from connection.config import base
from sqlalchemy.orm import relationship
from datetime import datetime

class outVaultRegistration(base):
    __tablename__ = "outvault"
    ref_Vault = Column(Integer,primary_key=True, autoincrement=True)
    ref_shift = Column(String(60), ForeignKey("shift.ref_shift"), nullable=False)
    quantity = Column(Float(), nullable=False)
    wname = Column(String(60), nullable=False)
    date = Column(DateTime, default=datetime.now)

    tshift = relationship("shiftRegistration", back_populates="toutflowVault")
