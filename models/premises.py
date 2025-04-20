from sqlalchemy import String, Column, Float, Boolean, ForeignKey, Enum, Integer
from connection.config import base
from sqlalchemy.orm import relationship

class premisesRegistration(base):
    __tablename__ = "premises"
    ref_premises = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(200), nullable=False, unique=True)
    password = Column(String(80), nullable=False)
    address = Column(String(80), nullable=False)
    vault = Column(Float(), default="0")
    type = Column(Enum("Servicio de reparacion de celulares","Venta de accesorios","Otro"), default="Servicio de reparacion de celulares", nullable=False)
    company = Column(String(50), ForeignKey('company.company_user'), nullable=False)
    active = Column(Boolean(), default="false")
    
    tcompany = relationship("companyRegistration", back_populates="tpremises")
    tshift = relationship("shiftRegistration", back_populates="tpremises")
    toutflowVault = relationship("outVaultRegistration", back_populates="tpremises")