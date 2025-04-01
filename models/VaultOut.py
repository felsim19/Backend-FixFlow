from sqlalchemy import String, Column, Float, ForeignKey, Integer
from connection.config import base
from sqlalchemy.orm import relationship

class outVaultRegistration(base):
    __tablename__ = "outVault"
    ref_Vault = Column(Integer,primary_key=True, autoincrement=True)
    ref_shift = Column(String(60), ForeignKey("shift.ref_shift"), nullable=False)
    quantity = Column(Float(), nullable=False)

    tshift = relationship("shiftRegistration", back_populates="toutflowVault")
