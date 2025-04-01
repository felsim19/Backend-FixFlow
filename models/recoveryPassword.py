from sqlalchemy import Column,DateTime,ForeignKey,String, Integer
from connection.config import base
from sqlalchemy.orm import relationship

class PasswordRecovery(base):
    __tablename__ = "password_recovery"
    id = Column(Integer, primary_key=True, index=True)
    company = Column(String(80), ForeignKey("company.company_user"), nullable=False)
    pin = Column(Integer, nullable=False)
    expires_at = Column(DateTime, nullable=False)

    tcompany = relationship("companyRegistration", back_populates="tpassword")