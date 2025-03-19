from sqlalchemy import String, Column
from connection.config import base
from sqlalchemy.orm import relationship

class companyRegistration(base):
    __tablename__ = "company"
    company_user = Column(String(60), primary_key=True)
    mail = Column(String(200), nullable=False, unique=True)
    password = Column(String(80), nullable=False)
    url_image = Column(String(100))
    
    tworker = relationship("workerRegistrastion", back_populates="tcompany")
    tbrand = relationship("brandsRegistration", back_populates="tcompany")