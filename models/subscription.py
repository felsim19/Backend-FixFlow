from sqlalchemy import Column, Date, Integer, Float, Enum, Boolean, String, ForeignKey
from connection.config import base
from sqlalchemy.orm import relationship


class SubscriptionRegistration(base):
    __tablename__ = "subscription"
    ref_subscription = Column(Integer, autoincrement=True, primary_key=True)
    company = Column(String(60), ForeignKey("company.company_user"), nullable=False)
    plan = Column(Enum("Basico", "Pro", "Premium"), nullable=False)
    price = Column(Float, nullable=False)
    date_start = Column(Date, nullable=False)
    paymentDate = Column(Date, nullable=False)
    added_premises = Column(Integer, nullable=False)
    active = Column(Boolean, nullable=False)

    tcompany = relationship("companyRegistration", back_populates="tsubscription")
