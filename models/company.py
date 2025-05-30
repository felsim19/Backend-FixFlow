from sqlalchemy import String, Column, Boolean, Integer
from connection.config import base
from sqlalchemy.orm import relationship

class companyRegistration(base):
    __tablename__ = "company"
    company_user = Column(String(60), primary_key=True)
    mail = Column(String(200), nullable=False, unique=True)
    password = Column(String(80), nullable=False)
    base_color = Column(String(50), default="#d84b17")
    number = Column(String(10), nullable=False)
    verifiedMail = Column(Boolean(), default=False) 
    nit = Column(String(20))
    quantity_premises = Column(Integer(), default=1)
    
    tworker = relationship("workerRegistration", back_populates="tcompany")
    tpassword = relationship("PasswordRecovery", back_populates="tcompany")
    tbrand = relationship("brandsRegistration", back_populates="tcompany")
    tpremises = relationship("premisesRegistration", back_populates="tcompany")
    tsubscription = relationship("SubscriptionRegistration", back_populates="tcompany")