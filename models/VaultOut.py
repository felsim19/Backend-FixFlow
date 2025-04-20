from sqlalchemy import String, Column, Float, ForeignKey, Integer, DateTime
from connection.config import base
from sqlalchemy.orm import relationship
from datetime import datetime

class outVaultRegistration(base):
    __tablename__ = "outvault"
    ref_Vault = Column(Integer,primary_key=True, autoincrement=True)
    ref_premises = Column(Integer, ForeignKey("premises.ref_premises"), nullable=False)
    quantity = Column(Float(), nullable=False)
    wname = Column(String(60), nullable=False)
    date = Column(DateTime, default=datetime.now)

    tpremises = relationship("premisesRegistration", back_populates="toutflowVault")
