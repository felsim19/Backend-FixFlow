from datetime import date
from sqlalchemy import String, Column, Enum, ForeignKey, Boolean, Date
from connection.config import base
from sqlalchemy.orm import relationship

class workerRegistration(base):
    __tablename__ = "worker"
    id = Column(String(80), primary_key=True, nullable=False)
    wname = Column(String(50), nullable=False)
    password = Column(String(80), nullable=False)
    document = Column(String(50), nullable=False)
    company = Column(String(50), ForeignKey('company.company_user'), nullable=False)
    wrole = Column(Enum("Gerente","Administrador","Tecnico"), default="Gerente", nullable=False)
    active = Column(Boolean, default="false")
    dateEntry = Column(Date, default=date.today)
    
    #Relacion birideccional hacia la company
    tcompany = relationship("companyRegistration", back_populates="tworker")
    tshift = relationship("shiftRegistration", back_populates="tworker") 