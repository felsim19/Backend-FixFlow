from sqlalchemy import Column, Date, Integer, Float, Enum, Boolean, String, ForeignKey
from connection.config import base
from sqlalchemy.orm import relationship


class SubscriptionRegistration(base):
    __tablename__ = "subscription"
    ref_subscription = Column(Integer, autoincrement=True, primary_key=True)
    company = Column(String(60), ForeignKey("company.company_user"), nullable=False)
    plan = Column(Enum("Venta", "Tecnico", "Distribuidor"))
    price = Column(Float)
    date_start = Column(Date)
    paymentDate = Column(Date)
    added_premises = Column(Integer)
    active = Column(Boolean)
    
    # Campos para información de pago
    payment_id = Column(String(100))
    payment_method = Column(String(50))
    payment_status = Column(String(50))


    tcompany = relationship("companyRegistration", back_populates="tsubscription")
