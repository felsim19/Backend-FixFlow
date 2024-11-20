from sqlalchemy import String, Column, Enum, ForeignKey
from connection.config import base
from sqlalchemy.orm import relationship

class workerRegistrastion(base):
    __tablename__ = "worker"
    wname = Column(String(50), nullable=False)
    password = Column(String(80), nullable=False)
    document = Column(String(50), primary_key=True, nullable=False)
    company = Column(String(50), ForeignKey('company.company_user'), nullable=False)
    wrole = Column(Enum("Gerente","Administrador","Colaborador"), default="Gerente", nullable=False)
    
    #Relacion birideccional hacia la company
    tcompany = relationship("companyRegistration", back_populates="tworker")
    tshift = relationship("shiftRegistration", back_populates="tworker") 